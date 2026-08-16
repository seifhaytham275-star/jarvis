import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import base64
from streamlit_mic_recorder import mic_recorder

# --- Page Setup & Styling ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖", layout="centered")

# CSS "Iron Man" Look
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #00ffcc; }
        .stChatInput { border: 2px solid #00ffcc !important; border-radius: 10px; }
        h1 { color: #00ffcc; text-align: center; text-shadow: 0 0 10px #00ffcc; }
        .stChatMessage { border-left: 3px solid #00ffcc; background-color: #1a1d23; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 J.A.R.V.I.S. Prime")

# --- Logic: Search ---
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except: return ""

# --- Logic: Voice ---
def play_smooth_voice(text):
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.rate = 1.1; 
            utterance.pitch = 1.0;
            let voices = window.speechSynthesis.getVoices();
            let v = voices.find(v => v.lang.includes('ar') || v.lang.includes('en'));
            if (v) utterance.voice = v;
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- Sidebar & Config ---
st.sidebar.title("⚙️ Configuration")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")

if st.sidebar.button("🗑️ Reset Chat"):
    st.session_state.messages = []
    st.rerun()

audio_info = mic_recorder(start_prompt="🎤 اضغط للتحدث", stop_prompt="⏹️ إيقاف", key='mic')

# --- Main Logic ---
if not groq_api_key:
    st.warning("دخل الـ API Key بتاع Groq عشان جارفيس يقوم!")
else:
    client = Groq(api_key=groq_api_key)
    if "messages" not in st.session_state: st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # File Upload & Chat
    uploaded_file = st.file_uploader("Upload Image...", type=["jpg", "png"])
    prompt = st.chat_input("أمرك يا سيدي...")

    user_input = prompt
    if audio_info:
        with st.spinner("بيسمع..."):
            try:
                user_input = client.audio.transcriptions.create(
                    file=("audio.wav", audio_info['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
            except: pass

    if user_input or uploaded_file:
        media_data = None
        if uploaded_file:
            media_data = f"data:{uploaded_file.type};base64,{base64.b64encode(uploaded_file.read()).decode('utf-8')}"
        
        st.session_state.messages.append({"role": "user", "content": user_input or "حلل الصورة دي"})
        with st.chat_message("user"): st.markdown(user_input or "صورة")

        with st.spinner("جارفيس بيفكر..."):
            search_context = search_web(user_input) if any(kw in (user_input or "").lower() for kw in ["سعر", "مين", "أخبار", "بحث"]) else ""
            
            system_prompt = (
                "You are J.A.R.V.I.S., sarcastic, sharp, witty. "
                "If Arabic: mix eloquent Arabic + Egyptian slang. If English: British accent. "
                f"Web Context: {search_context}"
            )
            
            # Request to Model
            chat_payload = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            response = client.chat.completions.create(messages=chat_payload, model="llama-3.3-70b-versatile")
            response_text = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
                play_smooth_voice(response_text)
