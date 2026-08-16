import streamlit as st
from groq import Groq
import re
from gtts import gTTS
import io
import base64
from streamlit_mic_recorder import mic_recorder

# --- Page Config ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖", layout="centered")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

if st.sidebar.button("➕ New Chat"):
    st.session_state.messages = []
    st.rerun()

# Voice Recorder widget in Sidebar
st.sidebar.markdown("---")
st.sidebar.write("🎙️ **Voice Command**")
audio_info = mic_recorder(start_prompt="🎤 اضغط للتحدث", stop_prompt="⏹️ إيقاف التسجيل", key='mic')

# --- Utility Functions (Dynamic Language TTS) ---
def text_to_speech_dynamic(text):
    try:
        clean_text = re.sub(r'http\S+', '', text)
        # Check if response contains Arabic text
        if re.search(r'[\u0600-\u06FF]', clean_text):
            tts = gTTS(text=clean_text, lang='ar')
        else:
            tts = gTTS(text=clean_text, lang='en', tld='co.uk')
            
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        return audio_io
    except Exception:
        return None

# --- Main Logic ---
if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar to activate J.A.R.V.I.S.")
else:
    try:
        client = Groq(api_key=api_key)
        
        # Isolated session state per browser/device tab
        if "messages" not in st.session_state: 
            st.session_state.messages = []

        # Render chat history
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("media_url"):
                    st.image(m["media_url"])
                if m.get("audio"):
                    st.audio(m["audio"], format='audio/mp3')

        uploaded_file = st.file_uploader("Upload Image (Optional)...", type=["jpg", "png", "jpeg"])
        prompt = st.chat_input("Ask J.A.R.V.I.S...")

        user_input = None

        # Handle text input or voice input
        if prompt:
            user_input = prompt
        elif audio_info:
            with st.spinner("Listening & Transcribing..."):
                try:
                    audio_bytes = audio_info['bytes']
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_bytes),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    user_input = transcription
                except Exception as e:
                    st.error(f"Voice transcription failed: {e}")

        if user_input or uploaded_file:
            final_input = user_input if user_input else "Analyze this image."
            media_data_url = None
            
            if uploaded_file:
                media_data_url = f"data:{uploaded_file.type};base64,{base64.b64encode(uploaded_file.read()).decode('utf-8')}"

            st.session_state.messages.append({"role": "user", "content": final_input, "media_url": media_data_url})
            
            with st.chat_message("user"):
                st.markdown(final_input)
                if media_data_url:
                    st.image(media_data_url)

            with st.spinner("Processing request..."):
                clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                response_text = ""
                
                low_input = final_input.lower()
                if any(keyword in low_input for keyword in ["genrate", "generate", "صورة", "photo", "image", "draw"]):
                    response_text = "يا سيدي أنا مساعد ذكي وعبقري مش معرض فني عشان أرسم لك طلبات غريبة. ركز معايا في المفيد!"
                elif media_data_url:
                    content_payload = [
                        {"type": "text", "text": f"You are J.A.R.V.I.S., sarcastic and witty. Reply in the exact same language the user speaks (if Arabic, reply in natural Arabic. If English, reply in English). {final_input}"},
                        {"type": "image_url", "image_url": {"url": media_data_url}}
                    ]
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": content_payload}], 
                        model="llama-3.2-11b-vision-preview"
                    )
                    response_text = chat.choices[0].message.content
                else:
                    system_prompt = (
                        "You are J.A.R.V.I.S., a brutally sarcastic, razor-sharp, and witty AI assistant. "
                        "CRITICAL INSTRUCTION: Detect the language of the user's message. If the user speaks Arabic, you MUST reply fluently, naturally, and intelligently in Arabic while maintaining your sharp, sarcastic, and witty personality. "
                        "If the user speaks English, reply in English with a British flair."
                    )
                    chat = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}] + clean_history + [{"role": "user", "content": final_input}],
                        model="llama-3.3-70b-versatile"
                    )
                    response_text = chat.choices[0].message.content

                audio_bytes = text_to_speech_dynamic(response_text)

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text, 
                    "audio": audio_bytes
                })
                
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')

    except Exception as e:
        st.error(f"An error occurred: {e}. Please check your API key or try again.")
