import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import base64
from streamlit_mic_recorder import mic_recorder

# --- Page Setup ---
st.set_page_config(page_title="J.A.R.V.I.S. Prime", page_icon="🤖", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #00ffcc; }
        .stChatMessage { border-left: 3px solid #00ffcc; background-color: #1a1d23; }
        h1 { color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if "chats" not in st.session_state: st.session_state.chats = {"Chat 1": []}
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"
if "settings" not in st.session_state:
    st.session_state.settings = {"voice": True, "mix": True, "api_key": ""}

# --- Functions ---
def play_smooth_voice(text):
    if not st.session_state.settings["voice"]: return
    # Forces Arabic pronunciation
    js_code = f"""<script>
        window.speechSynthesis.cancel();
        let u = new SpeechSynthesisUtterance("{text.replace('"', "'")}");
        u.lang = 'ar-SA'; 
        window.speechSynthesis.speak(u);
    </script>"""
    st.components.v1.html(js_code, height=0)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    tab1, tab2 = st.tabs(["💬 Chat History", "⚙️ Settings"])
    
    with tab2:
        st.session_state.settings["api_key"] = st.text_input("Groq API Key", type="password")
        st.session_state.settings["voice"] = st.toggle("Enable Voice Response", True)
        st.session_state.settings["mix"] = st.toggle("Mix Eloquent/Slang Arabic", True)
    
    with tab1:
        if st.button("➕ New Chat"):
            new_id = f"Chat {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_id] = []
            st.session_state.active_chat = new_id
        
        # Display chat list
        for chat_id in st.session_state.chats:
            if st.button(chat_id): st.session_state.active_chat = chat_id

# --- Main Interface ---
st.title("🤖 J.A.R.V.I.S. Prime")

# Render Active Chat
active = st.session_state.active_chat
for m in st.session_state.chats[active]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Input Section
audio_info = mic_recorder(key='mic', start_prompt="🎤 Hold to Speak")
prompt = st.chat_input("At your command, Sir...")

user_text = prompt
if audio_info and not prompt:
    with st.spinner("Listening..."):
        try:
            client = Groq(api_key=st.session_state.settings["api_key"])
            user_text = client.audio.transcriptions.create(file=("audio.wav", audio_info['bytes']), model="whisper-large-v3", response_format="text")
        except: pass

if user_text:
    st.session_state.chats[active].append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)
    
    with st.spinner("Thinking..."):
        system_prompt = "You are JARVIS. Use mixed Arabic/Sha'abi if enabled." if st.session_state.settings["mix"] else "Standard."
        client = Groq(api_key=st.session_state.settings["api_key"])
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.chats[active],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        st.session_state.chats[active].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
            play_smooth_voice(response)
