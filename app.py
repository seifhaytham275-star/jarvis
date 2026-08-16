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

# --- Authentication ---
if "user_email" not in st.session_state:
    st.title("🔐 يا هلا يا باشا.. سجل دخولك")
    email = st.text_input("اكتب إيميل الجيميل بتاعك:")
    if st.button("أدخل على السيستم"):
        if email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- Advanced Settings & Sidebar ---
st.sidebar.title("⚙️ الإعدادات")
api_key = st.sidebar.text_input("Groq API Key", type="password")
serper_key = st.sidebar.text_input("Serper Search API Key (Free)", type="password")
model_choice = st.sidebar.selectbox("الموديل", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

st.sidebar.markdown("---")
st.sidebar.subheader("📱 إعدادات واتساب (Twilio)")
twilio_sid = st.sidebar.text_input("Twilio Account SID", type="password")
twilio_token = st.sidebar.text_input("Twilio Auth Token", type="password")
whatsapp_number = st.sidebar.text_input("Twilio WhatsApp Number", value="whatsapp:+14155238886")

if st.sidebar.button("مسح الذاكرة"):
    conn = sqlite3.connect('jarvis_data.db')
    conn.execute("DELETE FROM messages WHERE email=?", (st.session_state.user_email,))
    conn.commit()
    conn.close()
    st.rerun()

st.title("🤖 جارفيس .. معاك يا سيف")

# --- Free Serper Web Search Function ---
def search_web(query):
    if not serper_key:
        return ""
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': serper_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        res_json = response.json()
        
        # جمع النتائج والـ snippets
        snippets = []
        if "organic" in res_json:
            for item in res_json["organic"][:3]:
                if "snippet" in item:
                    snippets.append(item["snippet"])
        return "\n".join(snippets)
    except Exception as e:
        return ""

# --- Chat Interface ---
messages = load_messages(st.session_state.user_email)
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("قولي يا بطل محتاج إيه؟...")

if prompt:
    save_message(st.session_state.user_email, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if not api_key:
        st.error("يا باشا نسيت تحط الـ Groq API Key في السايدبار!")
    else:
        with st.spinner("جارفيس بيبحث في جوجل بدقة..."):
            try:
                search_data = ""
                if any(kw in prompt.lower() for kw in ["search", "latest", "news", "مين", "ايه", "سعر", "اخبار", "بحث", "إيه", "كام", "نتائج"]):
                    search_data = search_web(prompt)
                
                client = Groq(api_key=api_key)
                system_prompt = (
                    f"You are J.A.R.V.I.S., the ultimate personal assistant for Seif ({st.session_state.user_email}). "
                    "Your personality: You are Egyptian, friendly, witty, smart, and act like a real human friend. "
                    "Talk to Seif using the Egyptian dialect (Ammiya) naturally. "
                    "Use Egyptian expressions, be fun, but be professional and helpful when he asks for tech/data. "
                    f"\nReal-time Web Search Data: {search_data}"
                )
                chat_payload = [{"role": "system", "content": system_prompt}] + messages + [{"role": "user", "content": prompt}]
                
                response = client.chat.completions.create(
                    messages=chat_payload,
                    model=model_choice,
                    temperature=0.4
                )
                res_text = response.choices[0].message.content
                
                save_message(st.session_state.user_email, "assistant", res_text)
                with st.chat_message("assistant"):
                    st.markdown(res_text)
                st.rerun()
            except Exception as e:
                st.error(f"حصلت مشكلة يا سيف: {e}")
