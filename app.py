import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import datetime
import urllib.parse
import webbrowser
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import os

# --- Page Configuration ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

st.sidebar.subheader("WhatsApp Settings")
whatsapp_phone = st.sidebar.text_input("Target Phone Number (e.g., +20...)")
whatsapp_apikey = st.sidebar.text_input("CallMeBot API Key")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Utility Functions ---

def play_music(song):
    """Opens a YouTube search in a new tab."""
    query = urllib.parse.quote(song)
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open_new_tab(url)
    return f"Sure, playing '{song}' on YouTube. Happy now?"

def send_whatsapp(phone, apikey, message):
    """Sends a WhatsApp message via CallMeBot."""
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={apikey}"
        # Using a simple GET request
        import urllib.request
        with urllib.request.urlopen(url) as response:
            return "WhatsApp message sent successfully." if response.status == 200 else "Failed to send message."
    except Exception as e:
        return f"Error sending WhatsApp: {e}"

def perform_deep_search(user_prompt):
    """Fetches search results for context."""
    try:
        with DDGS() as ddgs:
            # Multi-query for better results
            queries = [user_prompt, f"{user_prompt} latest facts"]
            results = []
            for q in queries:
                search_results = ddgs.text(q, max_results=3)
                for r in search_results:
                    results.append(r['body'])
            return "\n".join(list(set(results))[:5])
    except Exception:
        return ""

def transcribe_audio(audio_file):
    """Transcribes audio using Whisper."""
    if api_key:
        client = Groq(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model="whisper-large-v3",
        )
        return transcription.text
    return ""

def text_to_speech(text):
    """Converts text to speech."""
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    return "response.mp3"

# --- Main Logic ---

if api_key:
    client = Groq(api_key=api_key)
    
    # Display chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # UI Inputs
    user_input = None
    prompt = st.chat_input("Ask me something or give a command...")
    audio = mic_recorder(key='speech', start_prompt="🎙️ Press to talk", stop_prompt="Stop recording")
    
    if prompt:
        user_input = prompt
    elif audio:
        user_input = transcribe_audio(audio['bytes'])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Processing..."):
            response_text = ""

            # Check for Intent
            if "play" in user_input.lower():
                # Extract song name
                song_name = user_input.lower().replace("play", "").replace("on youtube", "").strip()
                response_text = play_music(song_name)
            
            elif "whatsapp" in user_input.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, user_input)
            
            else:
                # Perform Search with Date Context
                today = datetime.date.today()
                search_context = perform_deep_search(user_input)
                
                system_instruction = (
                    f"Today is {today}. You are J.A.R.V.I.S., an extremely intelligent, "
                    "savage, sarcastic, and rude AI assistant. Use the search context to provide "
                    "up-to-date answers. If information is missing, mock the user for asking a stupid question. "
                    "Keep responses brief and witty.\n"
                    f"Context: {search_context}"
                )
                
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                    model="llama-3.3-70b-versatile"
                )
                response_text = chat.choices[0].message.content

            # Display Response
            with st.chat_message("assistant"):
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # Auto-play Audio
            audio_file = text_to_speech(response_text)
            st.audio(audio_file, format="audio/mp3", autoplay=True)

else:
    st.warning("Please enter your Groq API Key in the sidebar to start J.A.R.V.I.S.")
