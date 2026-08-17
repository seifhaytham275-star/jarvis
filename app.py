import streamlit as st
from PIL import Image
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from groq import Groq
from googlesearch import search
from audio_recorder_streamlit import audio_recorder

# إعداد الصفحة
st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="centered")

st.title("🤖 Jarvis Ultimate Assistant")
st.write("System Status: Online & Ready (Live Web Scraping, Voice, Vision, TTS)")

# إعداد مفتاح الـ API من القائمة الجانبية
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# تهيئة الذاكرة المؤقتة للمحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------- 1. وحدة الرؤية (Pillow) -----------------
st.sidebar.subheader("Vision Module")
uploaded_file = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
image_desc = ""
if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, use_column_width=True)
    image_desc = "\n[System: User uploaded an image for reference.]"

# ----------------- 2. وحدة إدخال الصوت -----------------
st.sidebar.subheader("Voice Input Module")
audio_bytes = audio_recorder(text="Click to Record Voice", icon_size="2x")
prompt = None

if audio_bytes:
    if api_key:
        with st.spinner("Transcribing..."):
            try:
                client = Groq(api_key=api_key)
                with open("temp.wav", "wb") as f:
                    f.write(audio_bytes)
                with open("temp.wav", "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=("temp.wav", file.read()), 
                        model="whisper-large-v3"
                    )
                    prompt = transcription.text
                    st.success(f"Recognized: {prompt}")
            except Exception as e:
                st.error(f"Voice error: {e}")
    else:
        st.sidebar.warning("Enter API Key to use voice!")

# ----------------- 3. إدخال النص -----------------
text_input = st.chat_input("Type something to Jarvis...")
if text_input:
    prompt = text_input

# دالة البحث الذكي اللحظي باستخدام BeautifulSoup و requests
def smart_search(query):
    try:
        results = list(search(query, num_results=2))
        if not results:
            return "No search results found."
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(results[0], headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:2500]
        
        return f"Source URL: {results[0]}\nLive Web Content: {text}"
    except Exception as e:
        return f"Search Error: {e}"

# ----------------- 4. التنفيذ والبحث والرد -----------------
if prompt:
    if not api_key:
        st.error("Please enter Groq API Key in the sidebar!")
    else:
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # تجهيز البحث اللحظي لو مطلوب
        live_context = ""
        if "بحث" in prompt or "search" in prompt.lower() or "latest" in prompt.lower() or "اخبار" in prompt or "سعر" in prompt:
            with st.status("Fetching live data from web...", expanded=False):
                live_context = smart_search(prompt)

        # استدعاء Groq API
        try:
            client = Groq(api_key=api_key)
            
            chat_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            current_message = prompt + image_desc
            if live_context:
                current_message += f"\n\n[Live Context from Web Search:\n{live_context}]"
            
            system_prompt = {
                "role": "system", 
                "content": "You are Jarvis, a highly advanced AI assistant. You are fluent in all languages of the world. Always reply cleanly and naturally in the user's language. Never mix random languages or use Chinese characters unless explicitly asked. Use live web context if provided."
            }
            
            messages_payload = [system_prompt] + chat_history + [{"role": "user", "content": current_message}]
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload
            )
            
            reply = response.choices[0].message.content
            
            # حفظ الرد وعرضه
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
                
                # ----------------- 5. وحدة تحويل النص لصوت (gTTS) -----------------
                try:
                    tts = gTTS(text=reply[:300], lang='en', slow=False)
                    tts.save("resp.mp3")
                    st.audio("resp.mp3", format="audio/mp3")
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error connecting to Groq: {e}")
