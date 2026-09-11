import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JARVIS AI // SEIF",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
    ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 90% 5%,
                rgba(0,255,225,0.09),
                transparent 30%
            ),
            radial-gradient(
                circle at 5% 95%,
                rgba(0,130,255,0.08),
                transparent 35%
            ),
            #05080f;
        color: #dffffb;
    }

    .main {
        background: transparent;
    }

    /* ======================================================
       HEADER
    ====================================================== */

    .jarvis-header {
        text-align: center;
        padding: 20px 0 25px 0;
    }

    .jarvis-title {
        color: #00ffe1;
        font-family: monospace;
        font-size: 42px;
        font-weight: 800;
        letter-spacing: 8px;
        margin: 0;

        text-shadow:
            0 0 5px #00ffe1,
            0 0 15px #00ffe1,
            0 0 35px rgba(0,255,225,0.45);
    }

    .jarvis-subtitle {
        color: #62828b;
        font-family: monospace;
        font-size: 11px;
        letter-spacing: 3px;
        margin-top: 8px;
    }

    /* ======================================================
       SIDEBAR
    ====================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #030a12 0%,
                #050d16 100%
            );

        border-right:
            1px solid rgba(0,255,225,0.15);
    }

    section[data-testid="stSidebar"] h2 {
        color: #00ffe1;
        font-family: monospace;
        letter-spacing: 3px;
    }

    /* ======================================================
       STATUS
    ====================================================== */

    .status-online {
        padding: 12px;
        border-radius: 8px;

        background:
            rgba(0,255,225,0.06);

        border:
            1px solid rgba(0,255,225,0.25);

        color: #00ffe1;
        font-family: monospace;
        text-align: center;
        letter-spacing: 2px;

        margin: 10px 0 20px 0;
    }

    .status-offline {
        padding: 12px;
        border-radius: 8px;

        background:
            rgba(255,60,60,0.05);

        border:
            1px solid rgba(255,60,60,0.20);

        color: #ff7070;
        font-family: monospace;
        text-align: center;
        letter-spacing: 2px;

        margin: 10px 0 20px 0;
    }

    /* ======================================================
       CHAT
    ====================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 5px 10px;
    }

    /* ======================================================
       INPUT
    ====================================================== */

    [data-testid="stChatInput"] {
        border-radius: 14px;
    }

    /* ======================================================
       BUTTONS
    ====================================================== */

    .stButton > button {
        border-radius: 9px;
        border: 1px solid rgba(0,255,225,0.25);
        background: rgba(0,255,225,0.04);
        color: #00ffe1;
        font-family: monospace;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #00ffe1;
        box-shadow:
            0 0 15px rgba(0,255,225,0.18);
    }

    /* ======================================================
       FOOTER
    ====================================================== */

    .jarvis-footer {
        text-align: center;
        color: #3d5961;
        font-family: monospace;
        font-size: 10px;
        letter-spacing: 2px;
        padding: 25px 0 10px 0;
    }

    /* ======================================================
       DIVIDER
    ====================================================== */

    hr {
        border-color: rgba(0,255,225,0.10) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = None

if "connected" not in st.session_state:
    st.session_state.connected = False


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="jarvis-header">
        <div class="jarvis-title">JARVIS AI</div>
        <div class="jarvis-subtitle">
            PERSONAL INTELLIGENCE SYSTEM // GEMINI POWERED
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## SYSTEM")

    st.caption("GEMINI CORE CONNECTION")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your Gemini API key...",
        help="The key is entered into this session and is not written into app.py.",
    )

    if st.session_state.connected:
        st.markdown(
            '<div class="status-online">● SYSTEM ONLINE</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-offline">● SYSTEM OFFLINE</div>',
            unsafe_allow_html=True,
        )

    if st.button(
        "⚡ CONNECT JARVIS",
        use_container_width=True,
    ):

        if not api_key.strip():

            st.session_state.connected = False
            st.session_state.client = None

            st.error("Please enter your Gemini API key.")

        else:

            try:

                new_client = genai.Client(
                    api_key=api_key.strip()
                )

                # Test the connection
                test_response = new_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Reply with exactly: ONLINE",
                    config=types.GenerateContentConfig(
                        max_output_tokens=10
                    ),
                )

                if test_response:

                    st.session_state.client = new_client
                    st.session_state.connected = True

                    st.success("JARVIS connected successfully.")

                    st.rerun()

            except Exception as e:

                st.session_state.client = None
                st.session_state.connected = False

                st.error(
                    "Connection failed. Check your API key and model access."
                )

    st.divider()

    # ========================================================
    # MODEL
    # ========================================================

    model_name = st.selectbox(
        "AI MODEL",
        [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ],
        index=0,
    )

    st.divider()

    # ========================================================
    # CONTROLS
    # ========================================================

    st.markdown("### JARVIS CORE")

    if st.session_state.connected:
        st.write("Status: **ONLINE**")
    else:
        st.write("Status: **OFFLINE**")

    st.write("Engine: **Google Gemini**")
    st.write("Mode: **Personal Assistant**")
    st.write("Interface: **Cyber Terminal**")

    st.divider()

    if st.button(
        "🗑 CLEAR CONVERSATION",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption(
        "SECURITY NOTICE\n\n"
        "Never publish your API key in source code, GitHub, "
        "or screenshots."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Talk to JARVIS..."
)


# ============================================================
# PROCESS MESSAGE
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Check connection
    # --------------------------------------------------------

    if not st.session_state.connected:

        st.warning(
            "JARVIS is offline. Enter your Gemini API key "
            "in the SYSTEM sidebar and connect first."
        )

        st.stop()

    # --------------------------------------------------------
    # Store user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # --------------------------------------------------------
    # Prepare Gemini history
    # --------------------------------------------------------

    contents = []

    for message in st.session_state.messages:

        role = message["role"]

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
                        text=message["content"]
                    )
                ],
            )
        )

    # --------------------------------------------------------
    # Generate response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            response = (
                st.session_state.client
                .models
                .generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.8,
                        top_p=0.95,
                        max_output_tokens=4096,
                    ),
                )
            )

            if response and response.text:

                answer = response.text.strip()

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            else:

                st.error(
                    "Gemini returned an empty response."
                )

        except Exception as e:

            st.error(
                "JARVIS encountered an error while "
                "communicating with Gemini."
            )

            # Useful for debugging in Streamlit logs
            print(f"Gemini error: {e}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="jarvis-footer">
        JARVIS ONLINE // GEMINI CORE // SEIF'S PROJECT
    </div>
    """,
    unsafe_allow_html=True,
)
