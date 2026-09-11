import os
import logging
import gradio as gr
from google import genai
from google.genai import types

# ============================================================
# JARVIS AI — Configuration
# ============================================================

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Add it as a Hugging Face Space Secret or environment variable."
    )

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS")

# Gemini client
client = genai.Client(api_key=API_KEY)


# ============================================================
# JARVIS Personality
# ============================================================

SYSTEM_INSTRUCTION = """
You are JARVIS, Seif's personal AI assistant.

PERSONALITY:
- Intelligent, witty, calm, confident, and helpful.
- Natural and human-like, never robotic.
- Friendly and conversational.
- Practical: prioritize useful answers over unnecessary explanations.
- Be honest when you don't know something.
- Never claim to have performed an action you cannot actually perform.

LANGUAGE:
- If the user speaks Egyptian Arabic, reply in natural Egyptian Arabic.
- If the user speaks English, reply in natural modern English.
- If the user mixes Arabic and English, naturally match the style.
- Avoid awkward literal translations.
- Do not use emojis unless the user specifically asks for them.

STYLE:
- Keep simple questions concise.
- For technical questions, provide structured explanations and code when useful.
- Use Markdown when it improves readability.
- Do not repeatedly say "يا سيف" in every response.
"""


# ============================================================
# Helpers
# ============================================================

def normalize_history(history):
    """
    Convert Gradio chat history into Gemini-compatible contents.
    Supports both older tuple-style history and newer message-style history.
    """

    contents = []

    if not history:
        return contents

    for item in history:

        # New Gradio format:
        # {"role": "user", "content": "..."}
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")

            if role not in ("user", "assistant"):
                continue

            if not isinstance(content, str):
                continue

            if not content.strip():
                continue

            gemini_role = "user" if role == "user" else "model"

            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part(text=content)]
                )
            )

        # Old Gradio format:
        # ("user message", "assistant message")
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user_message, assistant_message = item

            if user_message:
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=str(user_message))]
                    )
                )

            if assistant_message:
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part(text=str(assistant_message))]
                    )
                )

    return contents


# ============================================================
# Main AI Function
# ============================================================

def predict(message, history):
    """
    Generate a response from Gemini using the current conversation.
    """

    if not message or not message.strip():
        return "اكتبلي حاجة الأول 😄"

    try:
        contents = normalize_history(history)

        # Add current user message
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(text=message.strip())
                ]
            )
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=2048,
            ),
        )

        if not response or not response.text:
            return "حصلت مشكلة ومفيش رد من Gemini. جرّب تاني."

        return response.text.strip()

    except Exception as e:
        logger.exception("Gemini request failed")

        # Don't expose internal API/configuration details to users
        return (
            "حصلت مشكلة وأنا بحاول أتصل بـ Gemini.\n\n"
            "اتأكد إن الـ API key شغال وإن الـ model متاح، وبعدها جرّب تاني."
        )


# ============================================================
# Custom Cyberpunk UI
# ============================================================

CUSTOM_CSS = r"""
/* =========================
   Global
========================= */

body,
.gradio-container {
    background:
        radial-gradient(circle at top right, #082b35 0%, transparent 35%),
        radial-gradient(circle at bottom left, #071b2c 0%, transparent 40%),
        #05080f !important;

    color: #d9ffff !important;
    font-family:
        "JetBrains Mono",
        "Fira Code",
        "Consolas",
        monospace !important;
}

/* =========================
   Main Container
========================= */

.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* =========================
   Header
========================= */

#jarvis-title {
    text-align: center;
    padding: 25px 10px 5px;
}

#jarvis-title h1 {
    color: #00ffe1 !important;
    font-size: 34px !important;
    font-weight: 800 !important;
    letter-spacing: 5px !important;

    text-shadow:
        0 0 5px #00ffe1,
        0 0 15px #00ffe1,
        0 0 35px rgba(0, 255, 225, 0.45);
}

#jarvis-subtitle {
    text-align: center;
    color: #789da5 !important;
    font-size: 13px !important;
    letter-spacing: 1px;
}

/* =========================
   Chat Window
========================= */

.chatbot {
    border:
        1px solid rgba(0, 255, 225, 0.25) !important;

    border-radius: 18px !important;

    background:
        rgba(3, 10, 18, 0.88) !important;

    box-shadow:
        0 0 25px rgba(0, 255, 225, 0.08),
        inset 0 0 30px rgba(0, 255, 225, 0.025) !important;
}

/* =========================
   Messages
========================= */

.message {
    border-radius: 14px !important;
}

.user {
    background:
        linear-gradient(
            135deg,
            rgba(0, 255, 225, 0.13),
            rgba(0, 120, 255, 0.08)
        ) !important;

    border: 1px solid rgba(0, 255, 225, 0.16) !important;
}

.bot {
    background:
        rgba(10, 18, 28, 0.9) !important;

    border:
        1px solid rgba(0, 255, 225, 0.10) !important;
}

/* =========================
   Input
========================= */

textarea {
    background: #050c14 !important;
    color: #dffffb !important;

    border:
        1px solid rgba(0, 255, 225, 0.25) !important;

    border-radius: 14px !important;
}

textarea:focus {
    border-color: #00ffe1 !important;

    box-shadow:
        0 0 12px rgba(0, 255, 225, 0.18) !important;
}

/* =========================
   Buttons
========================= */

button {
    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease !important;
}

button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 0 15px rgba(0, 255, 225, 0.18) !important;
}

/* =========================
   Footer
========================= */

#jarvis-footer {
    text-align: center;
    color: #45636b !important;
    font-size: 11px !important;
    padding: 12px;
}
"""


# ============================================================
# Interface
# ============================================================

with gr.Blocks(
    theme=gr.themes.Monochrome(
        primary_hue="cyan",
        secondary_hue="blue",
        neutral_hue="slate",
    ),
    css=CUSTOM_CSS,
    title="JARVIS AI // SEIF",
) as demo:

    gr.HTML(
        """
        <div id="jarvis-title">
            <h1>JARVIS AI</h1>
        </div>

        <div id="jarvis-subtitle">
            PERSONAL INTELLIGENCE SYSTEM // GEMINI 2.5 FLASH
        </div>
        """
    )

    chatbot = gr.Chatbot(
        label="JARVIS",
        height=620,
        bubble_full_width=False,
        show_copy_button=True,
        render_markdown=True,
        placeholder="""
        <div style="text-align:center; padding:40px;">
            <h2 style="color:#00ffe1;">
                SYSTEM ONLINE
            </h2>
            <p style="color:#607d86;">
                JARVIS is ready.
            </p>
        </div>
        """,
    )

    gr.ChatInterface(
        fn=predict,
        chatbot=chatbot,
        textbox=gr.Textbox(
            placeholder="Talk to JARVIS...",
            container=True,
            scale=7,
        ),
        submit_btn="SEND",
        stop_btn="STOP",
        clear_btn="CLEAR",
    )

    gr.HTML(
        """
        <div id="jarvis-footer">
            JARVIS ONLINE • GEMINI POWERED • SEIF'S PROJECT
        </div>
        """
    )


# ============================================================
# Launch
# ============================================================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
    )
