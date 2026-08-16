import streamlit as st
from groq import Groq
import sqlite3
import re
import requests
import json

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
st.set_page_config(page_title="J.A.R.V.I.S. Prime", page_icon="🤖", layout="wide")

# --- Auth ---
if "user_email" not in st.session_state:
    st.title("🔐 سجل دخولك / Login")
    email = st.text_input("إيميلك / Email:")
    if st.button("دخول / Login"):
        if email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- Sidebar & Language Selector ---
st.sidebar.title("⚙️ الإعدادات / Settings")

# اختيار اللغة بشكل مباشر
language_mode = st.sidebar.selectbox("🌐 لغة الحوار / Language", ["العربية (المصرية)", "English"])

api_key = st.sidebar.text_input("Groq API Key", type="password")
serper_key = st.sidebar.text_input("Serper API Key", type="password")
model = st.sidebar.selectbox("الموديل / Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

if st.sidebar.button("مسح الذاكرة / Clear History"):
    conn = sqlite3.connect('jarvis_data.db')
    conn.execute("DELETE FROM messages WHERE email=?", (st.session_state.user_email,))
    conn.commit()
    conn.close()
    st.rerun()

# --- Dynamic Title based on Language ---
if language_mode == "العربية (المصرية)":
    st.title("🤖 جارفيس .. معاك يا سيف")
    chat_placeholder = "قولي يا بطل محتاج إيه..."
else:
    st.title("🤖 J.A.R.V.I.S. .. At your service, Seif")
    chat_placeholder = "Type your command, Sir..."

# --- Web Search ---
def search_web(query):
    if not serper_key: return ""
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, data=payload).json()
        return "\n".join([item["snippet"] for item in res.get("organic", [])[:3] if "snippet" in item])
    except: return ""

# --- Chat Logic ---
messages = load_messages(st.session_state.user_email)
for m in messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

prompt = st.chat_input(chat_placeholder)

if prompt:
    save_message(st.session_state.user_email, "user", prompt)
    with st.chat_message("user"): st.markdown(prompt)
    
    if not api_key:
        st.error("نسيت الـ API Key! / Missing API Key!")
    else:
        with st.spinner("جارفيس بيفكر... / Thinking..."):
            search_data = search_web(prompt)
            client = Groq(api_key=api_key)
            
            # توجيه جارفيس حسب اختيار اللغة في السايدبار
            if language_mode == "العربية (المصرية)":
                system_prompt = (
                    f"You are J.A.R.V.I.S., the ultimate personal assistant for Seif ({st.session_state.user_email}). "
                    "Talk to Seif using the Egyptian dialect (Ammiya) naturally. Be friendly, witty, smart, and Egyptian. "
                    "ABSOLUTELY NO Chinese or gibberish characters. "
                    f"Search Context: {search_data}"
                )
            else:
                system_prompt = (
                    f"You are J.A.R.V.I.S., the ultimate personal assistant for Seif ({st.session_state.user_email}). "
                    "Talk in professional, fluent English. Be concise, brilliant, and sophisticated. "
                    "ABSOLUTELY NO Chinese or gibberish characters. "
                    f"Search Context: {search_data}"
                )

            chat_payload = [{"role": "system", "content": system_prompt}] + messages + [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(messages=chat_payload, model=model, temperature=0.3)
            res_text = response.choices[0].message.content
            
            # فلتر يمنع ظهور أي حروف غريبة أو صينية
            res_text = re.sub(r'[^\w\s\u0600-\u06FF.,!?-]', '', res_text)
            
            save_message(st.session_state.user_email, "assistant", res_text)
            with st.chat_message("assistant"): st.markdown(res_text)
            st.rerun()
