import os
import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖", layout="centered")
st.title("🤖 J.A.R.V.I.S. Assistant")
st.caption("Powered by Groq Cloud — 100% Free Tier")

# 2. Get API Key safely
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Groq API Key", type="password", help="Enter your gsk_... key here")
    if not api_key:
        st.info("Please enter your free Groq API key (from console.groq.com) in the sidebar to begin.", icon="🔑")
        st.stop()

# 3. Initialize Groq Client
client = Groq(api_key=api_key)

# 4. J.A.R.V.I.S. System Prompt
JARVIS_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are J.A.R.V.I.S., a highly intelligent, polite, and sophisticated AI assistant. "
        "You speak with refined composure, efficiency, and helpfulness. Address the user "
        "respectfully and provide accurate, structured, and helpful responses."
    )
}

# 5. Initialize Chat History in Session Memory
if "messages" not in st.session_state:
    st.session_state.messages = [JARVIS_SYSTEM_PROMPT]

# 6. Display Chat History (Excluding System Prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. Chat Input and Streaming Response
if user_prompt := st.chat_input("How may I assist you today?"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Free model options: "llama-3.3-70b-versatile" or "deepseek-r1-distill-llama-70b"
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error communicating with Groq API: {e}")
