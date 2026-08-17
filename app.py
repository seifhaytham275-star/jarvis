import base64
import io
import requests
from gtts import gTTS
import google.generativeai as genai
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Jarvis Web AI", page_icon="🌐", layout="centered")
st.title("🌐 Jarvis AI | Live Search Companion")

# 2. Hardcoded Serper API Key & Sidebar Configuration
SEARCH_API_KEY = "1a0f4872c2d6980e9cfcb5ddbab95990293333d5"

st.sidebar.title("⚙️ Jarvis Settings")
gemini_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# 3. British Accent Audio Function
def speak(text):
    try:
        tts = gTTS(text=text, lang="en", tld="co.uk")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

# 4. Live Web Search Function (Serper API)
def search_web(query):
    try:
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': SEARCH_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {"q": query}
        response = requests.post(url, headers=headers, json=payload).json()
        
        organic_results = response.get("organic", [])[:3]
        snippets = [f"- {item.get('title')}: {item.get('snippet')}" for item in organic_results]
        return "\n".join(snippets)
    except Exception:
        return ""

# 5. System Persona and Memory Management
SYSTEM_INSTRUCTION = """
You are Jarvis, Seif's witty, highly intelligent, and loyal British AI personal assistant.
- Use the live web search context provided to deliver accurate and up-to-date answers.
- Speak in a natural, refined British tone (use 'Sir', 'Splendid', 'Brilliant', 'Right away, Seif').
- Keep the conversation interactive, engaging, and friendly.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, Seif. Web search systems are active. How may I assist you today, sir?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. User Input Processing
if user_input := st.chat_input("Ask Jarvis or search anything..."):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if not gemini_key:
        reply = "Please enter your Gemini API key in the sidebar, Seif!"
    else:
        try:
            web_data = search_web(user_input)
            
            prompt = f"User Question: {user_input}\n"
            if web_data:
                prompt += f"\nLive Search Results from Web:\n{web_data}\n"

            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION)
            
            # Rebuild Chat History for Gemini Memory
            gemini_history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt)
            reply = response.text
        except Exception:
            reply = "I encountered a connection issue while reaching the search servers, Seif."

    with st.chat_message("assistant"):
        st.markdown(reply)
        speak(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
