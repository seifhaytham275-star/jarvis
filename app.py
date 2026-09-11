import gradio as gr
from google import genai
from google.genai import types


# ============================================================
# JARVIS CONFIG
# ============================================================

SYSTEM_INSTRUCTION = """
You are JARVIS, Seif's personal AI assistant.

PERSONALITY:
- Intelligent, witty, calm, confident, and helpful.
- Natural and human-like, never robotic.
- Friendly and conversational.
- Practical and direct.
- Be honest when you don't know something.
- Never claim to have performed an action you cannot perform.

LANGUAGE:
- If the user speaks Egyptian Arabic, reply in natural Egyptian Arabic.
- If the user speaks English, reply in natural modern English.
- If the user mixes Arabic and English, naturally match the style.

STYLE:
- Keep simple questions concise.
- For technical questions, provide useful explanations and code.
- Use Markdown when useful.
- Do not use emojis unless explicitly requested.
"""


# ============================================================
# GLOBAL CLIENT
# ============================================================

client = None


# ============================================================
# CONNECT GEMINI
# ============================================================

def connect_api(api_key):
    global client

    if not api_key or not api_key.strip():
        return (
            "🔴 DISCONNECTED",
            "Please enter your Gemini API key."
        )

    try:
        test_client = genai.Client(api_key=api_key.strip())

        # Save only after successful initialization
        client = test_client

        return (
            "🟢 ONLINE",
            "Gemini connection established successfully."
        )

    except Exception as e:
        client = None

        return (
            "🔴 ERROR",
            f"Could not connect to Gemini.\n\n{str(e)}"
        )


# ============================================================
# CHAT FUNCTION
# ============================================================

def predict(message, history, model_name):
    global client

    if client is None:
        return (
            "🔴 JARVIS is not connected.\n\n"
            "Open the SYSTEM sidebar, enter your Gemini API key, "
            "and press CONNECT."
        )

    if not message or not message.strip():
        return ""

    try:
        contents = []

        # Convert Gradio history to Gemini format
        if history:

            for item in history:

                # New Gradio message format
                if isinstance(item, dict):

                    role = item.get("role")
                    content = item.get("content")

                    if role not in ("user", "assistant"):
                        continue

                    if not isinstance(content, str):
                        continue

                    if not content.strip():
                        continue

                    gemini_role = (
                        "user"
                        if role == "user"
                        else "model"
                    )

                    contents.append(
                        types.Content(
                            role=gemini_role,
                            parts=[
                                types.Part(
                                    text=content
                                )
                            ],
                        )
                    )

                # Old tuple format
                elif isinstance(item, (list, tuple)) and len(item) == 2:

                    user_message, assistant_message = item

                    if user_message:
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part(
                                        text=str(user_message)
                                    )
                                ],
                            )
                        )

                    if assistant_message:
                        contents.append(
                            types.Content(
                                role="model",
                                parts=[
                                    types.Part(
                                        text=str(assistant_message)
                                    )
                                ],
                            )
                        )

        # Current message
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=message.strip()
                    )
                ],
            )
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=4096,
            ),
        )

        if not response or not response.text:
            return "JARVIS received an empty response."

        return response.text.strip()

    except Exception as e:

        return (
            "⚠️ **JARVIS ERROR**\n\n"
            "Something went wrong while communicating with Gemini.\n\n"
            f"`{str(e)}`"
        )


# ============================================================
# CSS
# ============================================================

CUSTOM_CSS = """
body {
    background:
        radial-gradient(
            circle at top right,
            #082d36 0%,
            transparent 35%
        ),
        radial-gradient(
            circle at bottom left,
            #071b2c 0%,
            transparent 40%
        ),
        #05080f !important;

    color: #dffffb !important;

    font-family:
        "JetBrains Mono",
        "Fira Code",
        Consolas,
        monospace !important;
}


.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
}


/* =========================
   HEADER
========================= */

#jarvis-header {
    text-align: center;
    padding: 20px;
}

#jarvis-header h1 {
    color: #00ffe1 !important;

    font-size: 36px !important;

    letter-spacing: 6px;

    text-shadow:
        0 0 5px #00ffe1,
        0 0 15px #00ffe1,
        0 0 35px rgba(0,255,225,.4);
}

#jarvis-header p {
    color: #66838b !important;

    font-size: 12px;

    letter-spacing: 2px;
}


/* =========================
   SIDEBAR
========================= */

#system-panel {
    background: rgba(3,10,18,.95) !important;

    border-right:
        1px solid rgba(0,255,225,.15) !important;
}

#system-title {
    color: #00ffe1 !important;

    font-size: 18px;

    letter-spacing: 3px;

    margin-bottom: 20px;
}


/* =========================
   STATUS
========================= */

#status {
    text-align: center;

    font-weight: bold;

    letter-spacing: 2px;

    padding: 10px;

    border-radius: 8px;

    background: rgba(0,255,225,.04);

    border:
        1px solid rgba(0,255,225,.15);
}


/* =========================
   CHAT
========================= */

.chatbot {
    background:
        rgba(3,10,18,.9) !important;

    border:
        1px solid rgba(0,255,225,.18) !important;

    border-radius: 18px !important;

    box-shadow:
        0 0 30px rgba(0,255,225,.06) !important;
}


/* =========================
   INPUT
========================= */

textarea {
    background: #050c14 !important;

    color: #dffffb !important;

    border:
        1px solid rgba(0,255,225,.25) !important;

    border-radius: 12px !important;
}

textarea:focus {
    border-color: #00ffe1 !important;

    box-shadow:
        0 0 15px rgba(0,255,225,.15) !important;
}


/* =========================
   BUTTONS
========================= */

button {
    transition:
        .15s ease !important;
}

button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 0 15px rgba(0,255,225,.18) !important;
}


/* =========================
   FOOTER
========================= */

#footer {
    text-align: center;

    color: #3e5961;

    font-size: 10px;

    padding: 10px;
}
"""


# ============================================================
# UI
# ============================================================

with gr.Blocks(
    title="JARVIS AI // SEIF",
    css=CUSTOM_CSS,
    theme=gr.themes.Monochrome(
        primary_hue="cyan",
        secondary_hue="blue",
        neutral_hue="slate",
    ),
) as demo:

    # -----------------------------
    # HEADER
    # -----------------------------

    gr.HTML(
        """
        <div id="jarvis-header">

            <h1>JARVIS AI</h1>

            <p>
                PERSONAL INTELLIGENCE SYSTEM //
                GEMINI POWERED
            </p>

        </div>
        """
    )

    # -----------------------------
    # SIDEBAR
    # -----------------------------

    with gr.Sidebar(
        position="left",
        width=320,
        open=True,
        elem_id="system-panel",
    ):

        gr.Markdown(
            "## SYSTEM",
            elem_id="system-title",
        )

        api_key = gr.Textbox(
            label="Gemini API Key",
            placeholder="AIza...",
            type="password",
            info="Your key is entered here and is not stored in the source code.",
        )

        connect_button = gr.Button(
            "⚡ CONNECT JARVIS",
            variant="primary",
        )

        status = gr.Textbox(
            value="🔴 DISCONNECTED",
            label="SYSTEM STATUS",
            interactive=False,
            elem_id="status",
        )

        status_message = gr.Markdown(
            "Enter your Gemini API key to initialize JARVIS."
        )

        gr.Markdown("---")

        model = gr.Dropdown(
            choices=[
                "gemini-2.5-flash",
                "gemini-2.5-pro",
            ],
            value="gemini-2.5-flash",
            label="AI MODEL",
        )

        gr.Markdown(
            """
            ### JARVIS CORE

            **Status:** Awaiting connection

            **Engine:** Google Gemini

            **Mode:** Personal Assistant

            **Interface:** Cyberpunk Terminal
            """
        )

        gr.Markdown("---")

        gr.Markdown(
            """
            ⚠️ **Security**

            Never share your API key with anyone.

            For a public Hugging Face Space,
            environment Secrets are safer than
            entering a key through the UI.
            """
        )

    # -----------------------------
    # CHAT
    # -----------------------------

    chatbot = gr.Chatbot(
        label="JARVIS",
        height=650,
        bubble_full_width=False,
        show_copy_button=True,
        render_markdown=True,
    )

    textbox = gr.Textbox(
        placeholder="Talk to JARVIS...",
        show_label=False,
        lines=2,
    )

    with gr.Row():

        send = gr.Button(
            "SEND",
            variant="primary",
            scale=2,
        )

        clear = gr.Button(
            "CLEAR",
            scale=1,
        )

    # -----------------------------
    # EVENTS
    # -----------------------------

    connect_button.click(
        fn=connect_api,
        inputs=[api_key],
        outputs=[status, status_message],
    )

    textbox.submit(
        fn=predict,
        inputs=[textbox, chatbot, model],
        outputs=chatbot,
    ).then(
        lambda: "",
        outputs=textbox,
    )

    send.click(
        fn=predict,
        inputs=[textbox, chatbot, model],
        outputs=chatbot,
    ).then(
        lambda: "",
        outputs=textbox,
    )

    clear.click(
        lambda: [],
        outputs=chatbot,
    )

    # -----------------------------
    # FOOTER
    # -----------------------------

    gr.HTML(
        """
        <div id="footer">
            JARVIS ONLINE // GEMINI CORE //
            SEIF'S PROJECT
        </div>
        """
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )
