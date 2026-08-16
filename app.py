        import streamlit as st
from groq import Groq
import sqlite3
import re
from streamlit_mic_recorder import mic_recorder

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect('jarvis_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (email TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def save_message(email, role, content):
    conn = sqlite3.connect('jarvis_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages VALUES (?, ?, ?)", (email, role, content))
    conn.commit()
    conn.close()

def load_messages(email):
    conn = sqlite3.connect('jarvis_data.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE email=?", (email,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1].decode('utf-8', 'ignore') if isinstance(r[1], bytes) else r[1]} for r in rows]

init_db()

# --- Page Setup ---
st.set_page_config(page_title="J.A.R.V.I.S. Prime", page_icon="🤖", layout="wide")

# --- Authentication ---
if "user_email" not in st.session_state:
    st.title("🔐 Authentication Required")
    email = st.text_input("Enter Gmail:")
    if st.button("Access System"):
        if email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- UI & Sidebar ---
st.sidebar.title("⚙️ System Settings")
api_key = st.sidebar.text_input("Groq API Key", type="password")
model = st.sidebar.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

if st.sidebar.button("Clear Memory"):
    conn = sqlite3.connect('jarvis_data.db')
    conn.execute("DELETE FROM messages WHERE email=?", (st.session_state.user_email,))
    conn.commit()
    conn.close()
    st.rerun()

st.title("🤖 J.A.R.V.I.S. Prime")

# --- Voice Input Feature ---
audio = mic_recorder(start_prompt="Record Command", stop_prompt="Stop Recording", key='recorder')
if audio:
    # Note: Transcription requires Whisper API, for now it placeholders as input
    st.info("Voice captured! Please type your command to proceed or integrate Whisper for STT.")

# --- Chat Interface ---
messages = load_messages(st.session_state.user_email)
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Command input...")

if prompt:
    save_message(st.session_state.user_email, "user", prompt)
    with st.chat_message("user"): st.markdown(prompt)
    
    if not api_key:
        st.error("Missing API Key!")
    else:
        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are J.A.R.V.I.S. Logical, concise, professional. "
                "Use English only. NEVER output nonsense or Chinese. "
                "Use Markdown tables/bullets for data."
            )
            chat_payload = [{"role": "system", "content": system_prompt}] + messages + [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(messages=chat_payload, model=model, temperature=0.2)
            res_text = response.choices[0].message.content
            res_text = re.sub(r'[^\x00-\x7F]+', '', res_text)
            
            save_message(st.session_state.user_email, "assistant", res_text)
            with st.chat_message("assistant"): st.markdown(res_text)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
