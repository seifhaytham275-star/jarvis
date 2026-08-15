import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import json
import urllib.request
import urllib.parse
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- Page Configuration ---
st.set_page_config(page_title="J.A.R.V.I.S. Ultimate Mode", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. Ultimate")
st.write("Savage, Deep Search, Voice, Text, and WhatsApp.")

# --- Sidebar Inputs ---
api_key = st.sidebar.text_input("Groq API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.subheader("WhatsApp Config (CallMeBot)")
whatsapp_phone = st.sidebar.text_input("Phone (e.g., +20...)")
whatsapp_apikey = st.sidebar.text_input("CallMeBot API Key")

if api_key:
    client = Groq(api_key=api_key)
    if "messages" not in st.session_state: st.session_state.messages = []

    # --- Functions ---
    def send_whatsapp(phone, apikey, message):
        try:
            encoded_msg = urllib.parse.quote(message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={apikey}"
            with urllib.request.urlopen(url) as response:
                return "WhatsApp message sent successfully." if response.status == 200 else "Failed to send."
        except Exception as e:
            return f"Error: {e}"

    def transcribe_audio(audio_file):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model="whisper-large-v3",
        )
        return transcription.text

    def text_to_speech(text):
        tts = gTTS(text=text, lang='ar')
        tts.save("response.mp3")
        return "response.mp3"

    def perform_deep_search(user_prompt):
        queries = [f"{user_prompt} 2026", "latest 2026 updates"]
        results_text = ""
        with DDGS() as ddgs:
            for q in queries:
                results = [r['body'] for r in ddgs.text(q, max_results=2)]
                results_text += "\n".join(results)
        return results_text

    # --- Display History ---
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # --- Input Handling ---
    user_input = None
    
    # Text Input
    if prompt := st.chat_input("Type something or talk..."):
        user_input = prompt
        
    # Voice Input
    audio = mic_recorder(key='speech', start_prompt="🎙️ Press to talk", stop_prompt="Stop")
    if audio:
        with st.spinner("Transcribing..."):
            user_input = transcribe_audio(audio['bytes'])

    # --- Process Input ---
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        with st.spinner("J.A.R.V.I.S. is processing..."):
            response_text = ""
            
            # Logic
            if "whatsapp" in user_input.lower() or "واتساب" in user_input.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, user_input)
            else:
                search_context = perform_deep_search(user_input)
                system_instruction = (
                    "You are J.A.R.V.I.S., extremely savage and sarcastic. "
                    "Use search context, keep Arabic, roast the user, and answer everything.\n"
                    f"{search_context}"
                )
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                    model="llama-3.1-70b-versatile"
                )
                response_text = chat.choices[0].message.content
            
            # Show Response
            with st.chat_message("assistant"): st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # Voice Output
            audio_file = text_to_speech(response_text)
            st.audio(audio_file, format="audio/mp3", autoplay=True)

else:
    st.warning("Enter your Groq API Key.")
