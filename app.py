import json
import os
import requests
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖", layout="centered")
st.title("🤖 J.A.R.V.I.S. Assistant")
st.caption("Just A Rather Very Intelligent System — Powered by DeepSeek")

# 2. Get API Key safely (checks Streamlit Secrets, Environment Variables, or Sidebar)
api_key = st.secrets.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("DeepSeek API Key", type="password", help="Enter your sk-... key here")
    if not api_key:
        st.info("Please enter your DeepSeek API key in the sidebar to begin, or add it to Streamlit Secrets.", icon="🔑")
        st.stop()

# 3. System Prompt for J.A.R.V.I.S.
JARVIS_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are J.A.R.V.I.S., a highly intelligent, polite, and sophisticated AI assistant. "
        "You speak with refined composure, efficiency, and helpfulness. Address the user "
        "respectfully and provide accurate, structured, and helpful responses."
    )
}

# 4. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [JARVIS_SYSTEM_PROMPT]

# 5. Render Chat History (Excluding System Prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. User Input & Streaming Response
if user_prompt := st.chat_input("How may I assist you today?"):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Stream DeepSeek AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": st.session_state.messages,
            "stream": True
        }

        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data_content = line_str[6:].strip()
                        if data_content == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_content)
                            content = chunk_json["choices"][0]["delta"].get("content", "")
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")
                        except json.JSONDecodeError:
                            continue

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with DeepSeek API: {e}")
