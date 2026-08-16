import streamlit as st
from groq import Groq
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

# --- JavaScript Native TTS for Smooth & Articulate Voice ("لَبَق") ---
def play_smooth_voice(text):
    # تنظيف النص من الروابط والرموز ليكون الكلام منساب ولَبَق
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); // إيقاف أي كلام قديم
            let utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.rate = 1.0; // سرعة طبيعية وواضحة
            utterance.pitch = 1.0; // نبرة متوازنة
            
            // محاولة اختيار أفضل صوت متاح في الجهاز (عربي أو إنجليزي)
            let voices = window.speechSynthesis.getVoices();
            let targetVoice = voices.find(v => v.lang.includes('ar') || v.lang.includes('en'));
            if (targetVoice) {{
                utterance.voice = targetVoice;
            }}
            
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- Main Logic ---
if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar to activate J.A.R.V.I.S.")
else:
    try:
        client = Groq(api_key=api_key)
        
        if "messages" not in st.session_state: 
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("media_url"):
                    st.image(m["media_url"])

        uploaded_file = st.file_uploader("Upload Image (Optional)...", type=["jpg", "png", "jpeg"])
        prompt = st.chat_input("Ask J.A.R.V.I.S...")

        user_input = None

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
                    response_text = "يا سيدي العزيز، أنا مساعد ذكي وعبقري مش معرض فني عشان أرسم لك! ركز معايا في المفيد."
                elif media_data_url:
                    content_payload = [
                        {"type": "text", "text": f"You are J.A.R.V.I.S., sarcastic and witty. If the user speaks Arabic, reply in a hilarious, sharp mix of eloquent Arabic and Egyptian street slang (فصحى على شعبي ساخر). {final_input}"},
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
                        "CRITICAL INSTRUCTION: If the user speaks Arabic, you MUST reply in a hilarious, razor-sharp, and witty mix of eloquent Arabic and Egyptian street/popular slang (فصحى مكسورة بعامية مصرية ساخرة وجامدة). "
                        "If the user speaks English, reply in English with a British flair."
                    )
                    chat = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}] + clean_history + [{"role": "user", "content": final_input}],
                        model="llama-3.3-70b-versatile"
                    )
                    response_text = chat.choices[0].message.content

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text
                })
                
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                    # تشغيل الصوت الناعم واللَبَق مباشرة من المتصفح
                    play_smooth_voice(response_text)

    except Exception as e:
5        st.error(f"An error occurred: {e}. Please check your API key or try again.")
