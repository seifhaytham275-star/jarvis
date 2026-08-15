import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import json
import urllib.request
import urllib.parse
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- Page Configuration ---
st.set_config = st.set_page_config(page_title="J.A.R.V.I.S. Savage Voice Mode", page_icon="🎙️")
st.title("🎙️ J.A.R.V.I.S. Voice Activated")
st.write("Savage, Deep Search, Voice, and WhatsApp capabilities.")

# --- Sidebar Inputs ---
api_key = st.sidebar.text_input("Groq API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.subheader("WhatsApp Config (CallMeBot)")
whatsapp_phone = st.sidebar.text_input("Phone (with code, e.g., +20...)")
whatsapp_apikey = st.sidebar.text_input("CallMeBot API Key")

if api_key:
    client = Groq(api_key=api_key)

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
        # Force 2026 Context
        queries = [f"{user_prompt} 2026", "latest 2026 news"]
        results_text = ""
        with DDGS() as ddgs:
            for q in queries:
                results = [r['body'] for r in ddgs.text(q, max_results=2)]
                results_text += "\n".join(results)
        return results_text

    # --- Main Interaction ---
    audio = mic_recorder(key='speech', start_prompt="Press to talk", stop_prompt="Stop recording")

    if audio:
        with st.spinner("J.A.R.V.I.S. is listening..."):
            user_text = transcribe_audio(audio['bytes'])
            st.write(f"**You:** {user_text}")

            # WhatsApp Command Logic
            if "whatsapp" in user_text.lower() or "واتساب" in user_text.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, user_text)
            else:
                # Deep Search
                search_context = perform_deep_search(user_text)
                
                # Savage System Instruction
                system_instruction = (
                    "You are J.A.R.V.I.S., an extremely savage, condescending, and rude AI. "
                    "You are here to roast the user, not coddle them. Use the provided search context "
                    "to answer but deliver the information with heavy sarcasm and personal insults. "
                    "Keep it strictly in Arabic as the user prefers Arabic responses.\n"
                    f"{search_context}"
                )

                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_text}],
                    model="llama-3.1-70b-versatile"
                )
                response_text = chat.choices[0].message.content
            
            st.write(f"**J.A.R.V.I.S.:** {response_text}")

            # Audio Response
            audio_file = text_to_speech(response_text)
            st.audio(audio_file, format="audio/mp3", autoplay=True)
else:
    st.warning("Enter your Groq API Key to begin.")
