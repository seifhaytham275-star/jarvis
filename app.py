import streamlit as st
from PIL import Image
import requests
from gtts import gTTS
from groq import Groq
from googlesearch import search
from audio_recorder_streamlit import audio_recorder

# إعداد الصفحة
st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="centered")

st.title("🤖 Jarvis Ultimate Assistant")
st.write("System Status: Online & Ready (Voice, Vision, Search, TTS)")

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

# ----------------- 4. التنفيذ والبحث والرد -----------------
if prompt:
    if not api_key:
        st.error("Please enter Groq API Key in the sidebar!")
    else:
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # تجهيز البحث لو المستخدم طلب بحث
        search_context = ""
        if "بحث" in prompt or "search" in prompt.lower():
            with st.status("Searching the web...", expanded=False):
                try:
                    urls = list(search(prompt, num_results=3))
                    search_context = f"\n\n[Web Search Results to help you answer: {urls}]"
                except Exception as e:
                    search_context = f"\n\n[Search Error: {e}]"

        # استدعاء Groq API
        try:
            client = Groq(api_key=api_key)
            
            # تجهيز المحادثة مع توجيه النظام لدعم كل اللغات
            chat_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            current_message = prompt + image_desc + search_context
            
            system_prompt = {
                "role": "system", 
                "content": "You are Jarvis, a highly advanced AI assistant. You are fluent in all languages of the world. Always reply cleanly and naturally in the user's language. Never mix random languages or use Chinese characters unless explicitly asked."
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
                    # نأخذ أول 300 حرف فقط عشان الصوت يتولد بسرعة
                    tts = gTTS(text=reply[:300], lang='en', slow=False)
                    tts.save("resp.mp3")
                    st.audio("resp.mp3", format="audio/mp3")
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error connecting to Groq: {e}")
