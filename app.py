import streamlit as st
from groq import Groq
import sqlite3
import re

# --- Database Setup ---
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
    return [{"role": r[0], "content": r[1]} for r in rows]

init_db()

# --- Page Setup ---
st.set_page_config(page_title="J.A.R.V.I.S.", page_icon="🤖", layout="wide")

# --- Authentication ---
if "user_email" not in st.session_state:
    st.title("🔐 Login Required")
    email = st.text_input("Enter your Gmail:")
    if st.button("Login"):
        if email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- Settings & WhatsApp Config ---
st.sidebar.title("⚙️ Settings")
api_key = st.sidebar.text_input("Groq API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📱 WhatsApp (Twilio) Config")
twilio_sid = st.sidebar.text_input("Twilio Account SID", type="password")
twilio_token = st.sidebar.text_input("Twilio Auth Token", type="password")
whatsapp_number = st.sidebar.text_input("Twilio WhatsApp Number", value="whatsapp:+14155238886")

if st.sidebar.button("Clear History"):
    conn = sqlite3.connect('jarvis_data.db')
    conn.execute("DELETE FROM messages WHERE email=?", (st.session_state.user_email,))
    conn.commit()
    conn.close()
    st.rerun()

st.title("🤖 J.A.R.V.I.S. Prime")

# --- Chat Interface ---
messages = load_messages(st.session_state.user_email)
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Enter your command...")

if prompt:
    save_message(st.session_state.user_email, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
    else:
        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are J.A.R.V.I.S. Logical, concise, professional. "
                "Use English only. NEVER output nonsense or Chinese."
            )
            chat_payload = [{"role": "system", "content": system_prompt}] + messages + [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                messages=chat_payload,
                model="llama-3.3-70b-versatile",
                temperature=0.2
            )
            res_text = response.choices[0].message.content
            res_text = re.sub(r'[^\x00-\x7F]+', '', res_text)
            
            save_message(st.session_state.user_email, "assistant", res_text)
            with st.chat_message("assistant"):
                st.markdown(res_text)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
