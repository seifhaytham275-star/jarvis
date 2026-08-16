import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import json
import urllib.request
import urllib.parse
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- Page Configuration ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar Inputs ---
api_key = st.sidebar.text_input("Groq API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.subheader("WhatsApp Configuration")
whatsapp_phone = st.sidebar.text_input("Phone Number (e.g., +20...)")
whatsapp_apikey = st.sidebar.text_input("CallMeBot API Key")

if api_key:
    client = Groq(api_key=api_key)
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # --- Utility Functions ---
    def send_whatsapp(phone, apikey, message):
        try:
            encoded_msg = urllib.parse.quote(message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={apikey}"
            with urllib.request.urlopen(url) as response:
                return "WhatsApp message sent successfully." if response.status == 200 else "Failed to send."
        except Exception as e:
            return f"Error sending WhatsApp: {e}"

    def transcribe_audio(audio_file):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model="whisper-large-v3",
        )
        return transcription.text

    def text_to_speech(text):
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        return "response.mp3"

    def perform_deep_search(user_prompt):
        try:
            with DDGS() as ddgs:
                # Multi-query strategy for better search depth
                queries = [user_prompt, f"{user_prompt} latest facts", f"{user_prompt} detailed summary"]
                results = []
                for q in queries:
                    search_results = ddgs.text(q, max_results=3)
                    for r in search_results:
                        results.append(r['body'])
                
                # Deduplicate and return top 6 unique results
                unique_results = list(set(results))
                return "\n".join(unique_results[:6])
        except Exception:
            return "Search service temporarily unavailable."

    # --- UI & Chat Handling ---
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    user_input = None
    if prompt := st.chat_input("Type something or talk..."): 
        user_input = prompt
        
    audio = mic_recorder(key='speech', start_prompt="🎙️ Press to talk", stop_prompt="Stop recording")
    if audio: 
        user_input = transcribe_audio(audio['bytes'])

    # --- Process Input ---
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): 
            st.markdown(user_input)

        with st.spinner("J.A.R.V.I.S. is processing..."):
            # Check for WhatsApp Command
            if "whatsapp" in user_input.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, user_input)
            else:
                search_context = perform_deep_search(user_input)
                
                # System Personality
                system_instruction = (
                    "You are J.A.R.V.I.S., an extremely intelligent, savage, sarcastic, and rude AI assistant. "
                    "DO NOT repeat search results verbatim. Use the provided search context to answer the user's question "
                    "succinctly and with wit. If the search context is irrelevant, ignore it and rely on your own knowledge.\n"
                    f"Context provided: {search_context}"
                )
                
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7
                )
                response_text = chat.choices[0].message.content
            
            # Display response
            with st.chat_message("assistant"): 
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # Text-to-Speech Output
            try:
                audio_file = text_to_speech(response_text)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
            except Exception:
                pass

else:
    st.warning("Please enter your Groq API Key in the sidebar to initiate J.A.R.V.I.S.")
