import streamlit as st
from openai import OpenAI
import urllib.parse
import requests
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
    st.session_state.settings = {"voice": True, "mix": True, "api_key": "", "serper_key": "", "mic_enabled": True}

# --- Functions (Serper Search) ---
def search_web_serper(query, serper_key):
    if not serper_key:
        return ""
    try:
        url = "https://google.serper.dev/search"
        payload = {"q": query, "gl": "eg", "hl": "ar"}
        headers = {
            "X-API-KEY": serper_key,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            snippets = []
            for item in data.get("organic", [])[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                snippets.append(f"- {title}: {snippet}")
            return "\n".join(snippets)
    except:
        pass
    return ""

def open_youtube_search(query):
    encoded_query = urllib.parse.quote(query)
    yt_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    js_code = f"""
    <script>
        window.open("{yt_url}", "_blank");
    </script>
    """
    st.components.v1.html(js_code, height=0)

def play_smooth_voice(text):
    if not st.session_state.settings["voice"]: return
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <div style="margin-top: 5px; margin-bottom: 5px;">
        <button onclick="speak()" style="background: #00ffcc; color: black; border: none; padding: 4px 10px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 12px;">
            🔊 Speak JARVIS
        </button>
    </div>
    <script>
        function speak() {{
            window.speechSynthesis.cancel();
            let u = new SpeechSynthesisUtterance("{clean_text}");
            u.lang = 'ar-SA'; 
            u.rate = 1.0;
            window.speechSynthesis.speak(u);
        }}
        speak();
    </script>
    """
    st.components.v1.html(js_code, height=60)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    tab1, tab2 = st.tabs(["💬 Chat History", "⚙️ Settings"])
    
    with tab2:
        # هنا هتدخل مفتاح DeepSeek API الخاص بك
        st.session_state.settings["api_key"] = st.text_input("DeepSeek API Key", type="password")
        st.session_state.settings["serper_key"] = st.text_input("Serper API Key", type="password")
        st.session_state.settings["voice"] = st.toggle("Enable Voice Response", True)
        st.session_state.settings["mic_enabled"] = st.toggle("Enable Microphone", True)
        st.session_state.settings["mix"] = st.toggle("Mix Eloquent/Slang Arabic", True)
    
    with tab1:
        if st.button("➕ New Chat"):
            new_id = f"Chat {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_id] = []
            st.session_state.active_chat = new_id
            st.rerun()
        
        for chat_id in st.session_state.chats:
            if st.button(chat_id):
                st.session_state.active_chat = chat_id
                st.rerun()

# --- Main Interface ---
st.title("🤖 J.A.R.V.I.S. Prime")

active = st.session_state.active_chat
for m in st.session_state.chats[active]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

audio_info = None
if st.session_state.settings.get("mic_enabled", True):
    audio_info = mic_recorder(key='mic', start_prompt="🎤 Hold to Speak")
else:
    st.info("🔒 Microphone is currently locked from Settings.")

prompt = st.chat_input("At your command, Sir...")

user_text = prompt
if audio_info and not prompt:
    api_key = st.session_state.settings.get("api_key")
    if not api_key:
        st.warning("Please enter your DeepSeek API Key in settings first!")
    else:
        # ملاحظة: لتحويل الصوت لنصوص يمكنك استخدام Groq Whisper أو تفعيل خاصية المتصفح، هنا سنترك الكود مرن
        st.info("Voice transcription requires a compatible audio endpoint; text input is fully active.")

if user_text:
    st.session_state.chats[active].append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)
    
    api_key = st.session_state.settings.get("api_key")
    serper_key = st.session_state.settings.get("serper_key")
    
    if not api_key or len(api_key) < 10:
        st.error("⚠️ Please enter a valid DeepSeek API Key in the Settings tab first!")
    else:
        with st.spinner("Thinking..."):
            try:
                lower_text = user_text.lower()
                if any(kw in lower_text for kw in ["يوتيوب", "youtube", "تشغيل", "فيديو", "watch", "play", "مروان"]):
                    open_youtube_search(user_text)

                search_context = search_web_serper(user_text, serper_key)
                
                system_prompt = (
                    "You are J.A.R.V.I.S., sarcastic, sharp, witty. Built by Seif. "
                    "If Arabic: mix eloquent Arabic with Egyptian street slang. If English: British accent. "
                    f"Google Search Context: {search_context}"
                )
                
                # ربط عميل OpenAI بـ DeepSeek API الأساسي
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                
                chat_payload = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.chats[active]]
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=chat_payload
                )
                response_text = response.choices[0].message.content
                
                st.session_state.chats[active].append({"role": "assistant", "content": response_text})
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                    play_smooth_voice(response_text)
            except Exception as e:
                st.error(f"Connection failed: {e}. Please check your DeepSeek API Key.")
