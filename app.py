import streamlit as st
import json
from datetime import datetime
from google import genai
from google.genai import types
import google_tools


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
- When live web search results are available to you, use them for anything
  time-sensitive, current, or fact-checkable, and don't rely on memory alone.
- If Gmail/Drive tools are available and the user asks about their email or
  files, use those tools rather than guessing. If a specific URL is given,
  use the URL context tool to actually read it before answering.
"""


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>

    :root {
        --bg-deep: #05090d;
        --panel: #0a1117;
        --panel-raised: #0d151d;
        --cyan: #33e8ff;
        --amber: #ffb238;
        --text-hi: #eaf6f8;
        --text-mid: #8fa3ab;
        --text-low: #4c6169;
        --line: rgba(51, 232, 255, 0.16);
    }

    /* ======================================================
       GLOBAL
    ====================================================== */

    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(51,232,255,0.07), transparent 32%),
            radial-gradient(circle at 8% 100%, rgba(255,178,56,0.05), transparent 38%),
            var(--bg-deep);
        color: var(--text-hi);
        font-family: 'IBM Plex Mono', monospace;
    }

    .main { background: transparent; }

    /* ======================================================
       HEADER
    ====================================================== */

    .jarvis-header {
        text-align: center;
        padding: 22px 0 0 0;
    }

    .jarvis-title {
        color: var(--text-hi);
        font-family: 'Chakra Petch', sans-serif;
        font-size: 40px;
        font-weight: 700;
        letter-spacing: 6px;
        margin: 0;
    }

    .jarvis-title span {
        color: var(--cyan);
        text-shadow: 0 0 18px rgba(51,232,255,0.55);
    }

    .jarvis-subtitle {
        color: var(--text-low);
        font-size: 11px;
        letter-spacing: 3px;
        margin-top: 6px;
    }

    .jarvis-scanline {
        height: 2px;
        margin: 18px auto 22px auto;
        max-width: 640px;
        background: linear-gradient(90deg, transparent, var(--cyan), transparent);
        background-size: 200% 100%;
        animation: scan 3.2s linear infinite;
        opacity: 0.7;
    }

    @keyframes scan {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ======================================================
       METRIC STRIP
    ====================================================== */

    .metric-strip {
        display: flex;
        gap: 10px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }

    .metric-chip {
        flex: 1;
        min-width: 150px;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 9px 14px;
    }

    .metric-chip .k {
        color: var(--text-low);
        font-size: 10px;
        letter-spacing: 2px;
    }

    .metric-chip .v {
        color: var(--text-hi);
        font-size: 13px;
        font-weight: 500;
        margin-top: 2px;
    }

    .metric-chip .v.on { color: var(--cyan); }
    .metric-chip .v.off { color: #ff6b6b; }

    /* ======================================================
       SIDEBAR
    ====================================================== */

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #030609 0%, #050b10 100%);
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--cyan);
        font-family: 'Chakra Petch', sans-serif;
        letter-spacing: 2px;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: var(--text-low);
    }

    /* ======================================================
       STATUS
    ====================================================== */

    .status-online, .status-offline {
        padding: 11px;
        border-radius: 4px;
        text-align: center;
        letter-spacing: 2px;
        font-size: 12px;
        margin: 10px 0 16px 0;
    }

    .status-online {
        background: rgba(51,232,255,0.06);
        border: 1px solid rgba(51,232,255,0.3);
        color: var(--cyan);
    }

    .status-offline {
        background: rgba(255,107,107,0.05);
        border: 1px solid rgba(255,107,107,0.25);
        color: #ff8a8a;
    }

    /* ======================================================
       CHAT
    ====================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 10px;
        padding: 4px 8px;
        background: transparent;
    }

    [data-testid="stChatMessageContent"] {
        border-radius: 10px;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: rgba(255,178,56,0.03);
        border-left: 2px solid rgba(255,178,56,0.35);
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background: rgba(51,232,255,0.03);
        border-left: 2px solid rgba(51,232,255,0.35);
    }

    /* ======================================================
       SUGGESTION CHIPS
    ====================================================== */

    .suggestion-label {
        color: var(--text-low);
        font-size: 11px;
        letter-spacing: 2px;
        margin: 4px 0 10px 2px;
    }

    /* ======================================================
       INPUT
    ====================================================== */

    [data-testid="stChatInput"] {
        border-radius: 10px;
        border: 1px solid var(--line);
    }

    /* ======================================================
       BUTTONS
    ====================================================== */

    .stButton > button {
        border-radius: 6px;
        border: 1px solid var(--line);
        background: var(--panel);
        color: var(--cyan);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        border-color: var(--cyan);
        background: rgba(51,232,255,0.08);
        box-shadow: 0 0 14px rgba(51,232,255,0.16);
        color: var(--text-hi);
    }

    /* ======================================================
       FOOTER
    ====================================================== */

    .jarvis-footer {
        text-align: center;
        color: var(--text-low);
        font-size: 10px;
        letter-spacing: 2px;
        padding: 28px 0 12px 0;
    }

    /* ======================================================
       DIVIDER
    ====================================================== */

    hr { border-color: var(--line) !important; }

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

if "last_error" not in st.session_state:
    st.session_state.last_error = None

if "connected_since" not in st.session_state:
    st.session_state.connected_since = None

if "google_connected" not in st.session_state:
    st.session_state.google_connected = google_tools.is_google_connected()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="jarvis-header">
        <div class="jarvis-title">JAR<span>VIS</span></div>
        <div class="jarvis-subtitle">
            PERSONAL INTELLIGENCE SYSTEM &nbsp;//&nbsp; GEMINI POWERED
        </div>
    </div>
    <div class="jarvis-scanline"></div>
    """,
    unsafe_allow_html=True,
)

status_label = "ONLINE" if st.session_state.connected else "OFFLINE"
status_class = "on" if st.session_state.connected else "off"
uptime_label = (
    st.session_state.connected_since.strftime("%H:%M")
    if st.session_state.connected_since
    else "--:--"
)
active_model = st.session_state.get("active_model", "—")

st.markdown(
    f"""
    <div class="metric-strip">
        <div class="metric-chip">
            <div class="k">STATUS</div>
            <div class="v {status_class}">{status_label}</div>
        </div>
        <div class="metric-chip">
            <div class="k">MODEL</div>
            <div class="v">{active_model}</div>
        </div>
        <div class="metric-chip">
            <div class="k">CONNECTED SINCE</div>
            <div class="v">{uptime_label}</div>
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

    if st.session_state.last_error:
        st.caption(f"Last error: {st.session_state.last_error}")

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
                    model="gemini-3.8-flash",
                    contents="Reply with exactly: ONLINE",
                    config=types.GenerateContentConfig(
                        max_output_tokens=10
                    ),
                )

                if test_response:

                    st.session_state.client = new_client
                    st.session_state.connected = True
                    st.session_state.last_error = None
                    st.session_state.connected_since = datetime.now()
                    st.session_state.active_model = "gemini-3.8-flash"

                    st.success("JARVIS connected successfully.")

                    st.rerun()

            except Exception as e:

                st.session_state.client = None
                st.session_state.connected = False
                st.session_state.last_error = str(e)

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
            "gemini-3.8-flash",
            "gemini-3.6-flash",
            "gemini-3.1-pro",
        ],
        index=0,
    )
    st.session_state.active_model = model_name

    temperature = st.slider(
        "CREATIVITY (temperature)",
        min_value=0.0,
        max_value=1.5,
        value=0.8,
        step=0.1,
    )

    web_search_enabled = st.toggle(
        "🔎 LIVE WEB SEARCH",
        value=True,
        help="Lets JARVIS search Google and cite sources before answering.",
    )

    url_reading_enabled = st.toggle(
        "🔗 READ LINKS I PASTE",
        value=True,
        help="Lets JARVIS fetch and read the actual content of URLs you give it.",
    )

    st.divider()

    st.markdown("### GOOGLE ACCESS")

    if st.session_state.google_connected:
        st.markdown(
            '<div class="status-online">● GMAIL + DRIVE LINKED</div>',
            unsafe_allow_html=True,
        )
        gmail_drive_enabled = st.toggle("📧 GMAIL + 📁 DRIVE", value=True)
    else:
        st.markdown(
            '<div class="status-offline">● GMAIL + DRIVE NOT LINKED</div>',
            unsafe_allow_html=True,
        )
        gmail_drive_enabled = False

        if st.button("🔗 CONNECT GOOGLE", use_container_width=True):
            try:
                google_tools.get_google_creds()
                st.session_state.google_connected = True
                st.success("Google account linked.")
                st.rerun()
            except FileNotFoundError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Google connection failed: {e}")

        st.caption("Needs a one-time setup — see GOOGLE_SETUP.md.")

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

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🗑 CLEAR", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col_b:
        chat_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            "💾 EXPORT",
            data=chat_json,
            file_name=f"jarvis_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    st.caption(
        "SECURITY NOTICE\n\n"
        "Never publish your API key in source code, GitHub, "
        "or screenshots."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

AVATARS = {"user": "🧑", "assistant": "⚡"}

for message in st.session_state.messages:

    with st.chat_message(message["role"], avatar=AVATARS.get(message["role"])):

        st.markdown(message["content"])

# ============================================================
# SUGGESTION CHIPS (only before the first message)
# ============================================================

if not st.session_state.messages:

    st.markdown('<div class="suggestion-label">TRY ASKING</div>', unsafe_allow_html=True)

    suggestions = [
        "Debug this Python error for me",
        "Summarize a long document",
        "Brainstorm names for a project",
    ]

    chip_cols = st.columns(len(suggestions))

    for col, suggestion in zip(chip_cols, suggestions):
        if col.button(suggestion, use_container_width=True, key=f"chip_{suggestion}"):
            st.session_state.pending_prompt = suggestion
            st.rerun()


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Talk to JARVIS..."
)

if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")


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

    with st.chat_message("user", avatar=AVATARS["user"]):
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
    # Generate response (with one automatic retry)
    # --------------------------------------------------------

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):

        answer = None
        last_exc = None
        grounding_sources = []

        gen_tools = []
        if web_search_enabled:
            gen_tools.append(types.Tool(google_search=types.GoogleSearch()))
        if url_reading_enabled:
            gen_tools.append(types.Tool(url_context=types.UrlContext()))
        if gmail_drive_enabled:
            gen_tools.extend([
                google_tools.search_gmail,
                google_tools.search_drive,
                google_tools.read_drive_file,
            ])
        if not gen_tools:
            gen_tools = None

        for attempt in range(2):

            try:

                response = (
                    st.session_state.client
                    .models
                    .generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=temperature,
                            top_p=0.95,
                            max_output_tokens=4096,
                            tools=gen_tools,
                        ),
                    )
                )

                if response and response.text:
                    answer = response.text.strip()

                    try:
                        candidate = response.candidates[0]
                        chunks = candidate.grounding_metadata.grounding_chunks
                        grounding_sources = [
                            c.web.uri for c in chunks if getattr(c, "web", None) and c.web.uri
                        ]
                    except (AttributeError, IndexError, TypeError):
                        grounding_sources = []

                    break

            except Exception as e:
                last_exc = e
                continue

        if answer:

            st.markdown(answer)

            if grounding_sources:
                with st.expander(f"🔎 {len(grounding_sources)} source(s) used"):
                    for src in grounding_sources:
                        st.markdown(f"- {src}")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        else:

            st.error(
                "JARVIS encountered an error while communicating with Gemini."
            )

            if last_exc:
                st.caption(f"Details: {last_exc}")
                print(f"Gemini error: {last_exc}")
            else:
                st.caption("Gemini returned an empty response.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="jarvis-footer">
        JARVIS &nbsp;//&nbsp; GEMINI CORE &nbsp;//&nbsp; SEIF'S PROJECT
    </div>
    """,
    unsafe_allow_html=True,
)
