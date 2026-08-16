import streamlit as st
from groq import Groq
import re
from gtts import gTTS
import io
import base64

# --- Page Config ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖", layout="centered")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

if st.sidebar.button("➕ New Chat"):
    st.session_state.messages = []
    st.rerun()

# --- Utility Functions ---
def text_to_british_speech(text):
    try:
        clean_text = re.sub(r'http\S+', '', text)
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
        
        # Initialize chat history in session state for isolation per device/browser tab
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

        # File uploader and chat input
        uploaded_file = st.file_uploader("Upload Image (Optional)...", type=["jpg", "png", "jpeg"])
        prompt = st.chat_input("Ask J.A.R.V.I.S...")

        if prompt or uploaded_file:
            user_input = prompt if prompt else "Analyze this image."
            media_data_url = None
            
            if uploaded_file:
                media_data_url = f"data:{uploaded_file.type};base64,{base64.b64encode(uploaded_file.read()).decode('utf-8')}"

            # Append user message
            st.session_state.messages.append({"role": "user", "content": user_input, "media_url": media_data_url})
            
            with st.chat_message("user"):
                st.markdown(user_input)
                if media_data_url:
                    st.image(media_data_url)

            # Generate response
            with st.spinner("Processing request..."):
                clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                response_text = ""
                
                low_input = user_input.lower()
                if any(keyword in low_input for keyword in ["genrate", "generate", "صورة", "photo", "image", "draw"]):
                    response_text = "I am an AI language and vision assistant, sir, not an art gallery. I deal in logic and sarcasm, not drawing random requests."
                elif media_data_url:
                    content_payload = [
                        {"type": "text", "text": f"You are J.A.R.V.I.S., sarcastic and witty. {user_input}"},
                        {"type": "image_url", "image_url": {"url": media_data_url}}
                    ]
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": content_payload}], 
                        model="llama-3.2-11b-vision-preview"
                    )
                    response_text = chat.choices[0].message.content
                else:
                    chat = client.chat.completions.create(
                        messages=[{"role": "system", "content": "You are J.A.R.V.I.S., a brutally sarcastic, razor-sharp, and witty AI assistant with a British flair."}] + clean_history + [{"role": "user", "content": user_input}],
                        model="llama-3.3-70b-versatile"
                    )
                    response_text = chat.choices[0].message.content

                audio_bytes = text_to_british_speech(response_text)

                # Append assistant message
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
