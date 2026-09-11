"""
JARVIS on WhatsApp — powered by Meta's official WhatsApp Cloud API + Google Gemini.

This is a SEPARATE server from the Streamlit app. It must run somewhere with
a public HTTPS URL (Meta needs to reach it), such as:
  - your own VPS / Render / Railway / Fly.io (free tiers exist)
  - locally + ngrok / cloudflared for testing

Setup summary (full guide in WHATSAPP_SETUP.md):
  1. Create a Meta Developer app -> add the "WhatsApp" product.
     Meta gives you a FREE test phone number instantly.
  2. From WhatsApp -> API Setup, copy:
       - PHONE_NUMBER_ID
       - a temporary Access Token (24h) or a permanent System User token
  3. Pick your own VERIFY_TOKEN (any random string you invent).
  4. Set the four environment variables below, then run this file.
  5. Expose it publicly (ngrok http 8080) and paste that HTTPS URL + your
     VERIFY_TOKEN into Meta's webhook configuration screen.
  6. Message your test number on WhatsApp from your personal phone
     (you must first add it as an allowed tester number in Meta's dashboard).
"""

from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import os
import requests

# ============================================================
# CONFIG — set these as environment variables (safer) or paste directly
# ============================================================

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "YOUR_WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "YOUR_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "choose_any_secret_string")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

GRAPH_API_VERSION = "v21.0"
WHATSAPP_SEND_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"

MODEL_NAME = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are JARVIS, Seif's personal AI assistant, now reachable on WhatsApp.

PERSONALITY:
- Intelligent, witty, calm, confident, and helpful.
- Natural and human-like, never robotic.
- Practical and direct. Be honest when you don't know something.
- Never claim to have performed an action you cannot perform.

LANGUAGE:
- If the user speaks Egyptian Arabic, reply in natural Egyptian Arabic.
- If the user speaks English, reply in natural modern English.
- If mixed, match their style naturally.

STYLE:
- Keep replies WhatsApp-appropriate: concise, no huge walls of text.
- Use simple formatting (WhatsApp supports *bold*, _italic_, not full Markdown).
- Do not use emojis unless explicitly requested.
"""

app = Flask(__name__)
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# Per-sender conversation memory (in-memory; resets on restart)
CONVERSATIONS = {}
MAX_HISTORY_TURNS = 12  # keep last N user+model turns per sender


# ============================================================
# WEBHOOK VERIFICATION (Meta calls this once when you save the config)
# ============================================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# ============================================================
# INCOMING MESSAGES
# ============================================================

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json(silent=True) or {}

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Ignore status updates (sent/delivered/read receipts) — only handle real messages
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]  # WhatsApp ID (phone number) of the sender

        if message.get("type") != "text":
            send_whatsapp_message(sender, "I can only read text messages for now, Seif.")
            return jsonify({"status": "ok"}), 200

        user_text = message["text"]["body"]

        reply = ask_jarvis(sender, user_text)
        send_whatsapp_message(sender, reply)

    except (KeyError, IndexError):
        # Not a message event we care about (e.g. delivery receipt) — ignore quietly
        pass
    except Exception as e:
        print(f"Webhook processing error: {e}")

    return jsonify({"status": "ok"}), 200


# ============================================================
# GEMINI
# ============================================================

def ask_jarvis(sender_id: str, user_text: str) -> str:
    history = CONVERSATIONS.setdefault(sender_id, [])

    history.append(types.Content(role="user", parts=[types.Part(text=user_text)]))
    history[:] = history[-MAX_HISTORY_TURNS * 2:]

    try:
        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=1024,
            ),
        )
        reply = (response.text or "").strip() or "I didn't catch that, Seif — try again?"
    except Exception as e:
        print(f"Gemini error: {e}")
        return "JARVIS core is having trouble reaching Gemini right now. Try again in a moment."

    history.append(types.Content(role="model", parts=[types.Part(text=reply)]))
    return reply


# ============================================================
# WHATSAPP SEND
# ============================================================

def send_whatsapp_message(to: str, body: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:4096]},  # WhatsApp text messages cap at 4096 chars
    }

    try:
        resp = requests.post(WHATSAPP_SEND_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code >= 400:
            print(f"WhatsApp send error [{resp.status_code}]: {resp.text}")
    except requests.RequestException as e:
        print(f"WhatsApp send request failed: {e}")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/")
def health():
    return "JARVIS WhatsApp bridge is running.", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
