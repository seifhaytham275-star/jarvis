import streamlit as st
from groq import Groq

st.set_page_config(page_title="Jarvis Secure Terminal", layout="centered")

with st.sidebar:
    st.markdown("### System Configuration")
    GROQ_API_KEY_INPUT = st.text_input("Groq API Key", type="password")
    selected_model = st.selectbox(
        "Choose Groq Model:",
        [
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]
    )

CORRECT_PASSWORD = "Sefo2011"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("### Access Control Gate")
    password_input = st.text_input("Authorization Key", type="password")
    if st.button("Authenticate"):
        if password_input == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop()

st.markdown("### JARVIS // Secure Terminal")

if not GROQ_API_KEY_INPUT:
    st.warning("Please enter your Groq API key in the sidebar.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY_INPUT)

SYSTEM_INSTRUCTION = """
You are Jarvis, Seif's advanced personal assistant.
- STYLE: Formal, precise, efficient. NO emojis allowed.
- LANGUAGES: Egyptian Arabic or British English depending on user input.
- DATA INITIALIZATION: Ingest, process, and retain any custom data or notes provided by Seif dynamically during the session.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Enter command or data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        completion = client.chat.completions.create(
            model=selected_model,
            messages=st.session_state.messages,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
