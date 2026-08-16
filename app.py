import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import datetime
import uuid
import re
from gtts import gTTS
import io
import base64
import tempfile
import cv2

# --- Page Config ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar ---
api_key = st.sidebar.text_input("Groq API Key", type="password")

if st.sidebar.button("➕ New Chat"):
    st.session_state.messages = []
    st.rerun()

# --- Utility Functions ---
def extract_video_frames(video_file, max_frames=3):
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(video_file.read())
        tfile.close()
        cap = cv2.VideoCapture(tfile.name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = [int(i * total_frames / (max_frames + 1)) for i in range(1, max_frames + 1)]
        base64_frames = []
        current_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            if current_frame in frame_indices:
                _, buffer = cv2.imencode('.jpg', frame)
                base64_frames.append(base64.b64encode(buffer).decode('utf-8'))
            current_frame += 1
        cap.release()
        return base64_frames
    except: return []

def text_to_british_speech(text):
    try:
        clean_text = re.sub(r'http\S+', '', text)
        tts = gTTS(text=clean_text, lang='en', tld='co.uk')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        return audio_io
    except: return None

# --- Main Logic ---
if api_key:
    client = Groq(api_key=api_key)
    
    # جلسة مستقلة لكل متصفح/جهاز
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("media_url"):
                if m.get("media_type") == "image": st.image(m["media_url"])
                elif m.get("media_type") == "video": st.video(m["media_url"])
            if m.get("audio"):
                st.audio(m["audio"], format='audio/mp3')

    uploaded_file = st.file_uploader("Upload Image or Video...", type=["jpg", "png", "mp4"])
    prompt = st.chat_input("Ask J.A.R.V.I.S...")

    if prompt or uploaded_file:
        user_input = prompt if prompt else "Analyze this."
        media_data_url, media_type, video_frames = None, None, []
        
        if uploaded_file:
            media_type = "image" if "image" in uploaded_file.type else "video"
            media_data_url = f"data:{uploaded_file.type};base64,{base64.b64encode(uploaded_file.read()).decode('utf-8')}"
            if media_type == "video":
                uploaded_file.seek(0)
                video_frames = extract_video_frames(uploaded_file)

        st.session_state.messages.append({"role": "user", "content": user_input, "media_url": media_data_url, "media_type": media_type})
        
        with st.chat_message("user"):
            st.markdown(user_input)
            if media_data_url:
                if media_type == "image": st.image(media_data_url)
                elif media_type == "video": st.video(media_data_url)

        with st.spinner("Processing..."):
            clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            response_text = ""
            
            if media_data_url:
                content_payload = [{"type": "text", "text": f"You are J.A.R.V.I.S., sarcastic and witty. {user_input}"}]
                if media_type == "image":
                    content_payload.append({"type": "image_url", "image_url": {"url": media_data_url}})
                elif media_type == "video":
                    for f in video_frames:
                        content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{f}"}})
                
                chat = client.chat.completions.create(messages=[{"role": "user", "content": content_payload}], model="llama-3.2-11b-vision-preview")
                response_text = chat.choices[0].message.content
            else:
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are J.A.R.V.I.S., a brutally sarcastic, razor-sharp, and witty AI assistant with a British flair."}] + clean_history + [{"role": "user", "content": user_input}],
                    model="llama-3.3-70b-versatile"
                )
                response_text = chat.choices[0].message.content

            audio_bytes = text_to_british_speech(response_text)

            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text, 
                "audio": audio_bytes
            })
            
            with st.chat_message("assistant"):
                st.markdown(response_text)
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/mp3')
else:
    st.warning("Please enter your Groq API Key.")
