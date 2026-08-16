import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import datetime
import urllib.parse
import webbrowser
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import sqlite3
import uuid

# --- Database Setup (Chat History) ---
def init_db():
    conn = sqlite3.connect('jarvis_chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (chat_id TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Page Configuration ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar Inputs ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

# --- Utility Functions ---

def play_music(song):
    """Opens YouTube in a new tab."""
    query = urllib.parse.quote(song)
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={query}")
    return f"I've queued up '{song}' on YouTube. Enjoy the music."

def perform_deep_search(user_prompt):
    """Fetches real-time info."""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(user_prompt, max_results=4)]
            return "\n".join(results)
    except: 
        return "Search service is currently unavailable."

# --- Main Logic ---

if api_key:
    client = Groq(api_key=api_key)
    
    # Initialize Session
    if "chat_id" not in st.session_state: 
        st.session_state.chat_id = str(uuid.uuid4())
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # Display History from Session
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # UI Inputs
    prompt = st.chat_input("Ask or command...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Save User Message to DB
        conn = sqlite3.connect('jarvis_chat.db')
        conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "user", prompt))
        conn.commit()
        conn.close()

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Analyzing..."):
            response_text = ""

            # Check for Intent
            if "play" in prompt.lower():
                song_name = prompt.lower().replace("play", "").strip()
                response_text = play_music(song_name)
            
            else:
                # Perform Search with Date Context
                today = datetime.date.today()
                search_context = perform_deep_search(prompt)
                
                # Sophisticated, clever, but helpful personality
                system_instruction = (
                    f"Today is {today}. You are J.A.R.V.I.S., a sophisticated, witty, and helpful AI assistant. "
                    "You have real-time access to search results. "
                    "Handle queries about 2026 as current events. Use the provided search context to answer accurately. "
                    "Be clever and charming in your responses, but never rude, insulting, or evasive. "
                    "If you don't know an answer, simply state that the information isn't available."
                    f"\nContext: {search_context}"
                )
                
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                    model="llama-3.3-70b-versatile"
                )
                response_text = chat.choices[0].message.content

            # Save Assistant Response to DB
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            conn = sqlite3.connect('jarvis_chat.db')
            conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "assistant", response_text))
            conn.commit()
            conn.close()

            with st.chat_message("assistant"):
                st.markdown(response_text)

else:
    st.warning("Please enter your Groq API Key in the sidebar to start.")
