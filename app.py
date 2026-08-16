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

# --- Auth & API Key Login Screen ---
if "user_email" not in st.session_state or "groq_api_key" not in st.session_state:
    st.title("🔐 تسجيل الدخول وإدخال المفاتيح / Login & API Keys")
    email = st.text_input("إيميلك / Email:")
    api_key_input = st.text_input("Groq API Key:", type="password")
    serper_key_input = st.text_input("Serper API Key (مهم للبحث ويوتيوب / Required for Search & YouTube):", type="password")
    
    if st.button("دخول / Login"):
        if email and api_key_input:
            st.session_state.user_email = email
            st.session_state.groq_api_key = api_key_input
            st.session_state.serper_key = serper_key_input
            st.rerun()
        else:
            st.error("يا بطل لازم تكتب الإيميل ومفتاح الـ Groq API Key عشان تدخل!")
    st.stop()

# Get keys from session
api_key = st.session_state.get("groq_api_key", "")
serper_key = st.session_state.get("serper_key", "")

# --- Sidebar & Settings ---
st.sidebar.title("⚙️ الإعدادات / Settings")

language_mode = st.sidebar.selectbox("🌐 لغة الحوار / Language", ["العربية (المصرية)", "English"])
model = st.sidebar.selectbox("الموديل / Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

st.sidebar.markdown("---")
if st.sidebar.button("تسجيل خروج / Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if st.sidebar.button("مسح الذاكرة / Clear History"):
    conn = sqlite3.connect('jarvis_data.db')
    conn.execute("DELETE FROM messages WHERE email=?", (st.session_state.user_email,))
    conn.commit()
    conn.close()
    st.rerun()

# --- Dynamic Title & Placeholder ---
if language_mode == "العربية (المصرية)":
    st.title("🤖 جارفيس .. معاك يا سيف")
    chat_placeholder = "قولي يا بطل محتاج إيه أو عايز فيديو إيه..."
else:
    st.title("🤖 J.A.R.V.I.S. .. At your service, Seif")
    chat_placeholder = "Type your command or search YouTube..."

# --- Web & YouTube Search ---
def search_web(query):
    if not serper_key: return ""
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, data=payload).json()
        
        results = []
        for item in res.get("organic", [])[:4]:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
        return "\n---\n".join(results)
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
        st.error("مفيش API Key! يرجى تسجيل الخروج وإعادة إدخال المفتاح.")
    else:
        with st.spinner("جارفيس بيفحث وبيجهّز اللينك... / Searching..."):
            search_data = search_web(prompt)
            client = Groq(api_key=api_key)
            
            if language_mode == "العربية (المصرية)":
                system_prompt = (
                    f"You are J.A.R.V.I.S., the ultimate personal assistant created by Seif Haytham. "
                    "CRITICAL INSTRUCTION 1: If anyone asks who created you, who made you, or 'مين اللي عملك', you MUST answer starting with: 'بص بس كده، اللي عملني هو العبقري سيف هيثم'. "
                    "CRITICAL INSTRUCTION 2: If the user asks for a video, song, or anything on YouTube, use the provided Search Context to extract the direct YouTube URL and present it clearly as a clickable Markdown link `[اسم الفيديو](الرابط)` so it opens directly in the YouTube app when clicked. "
                    "Talk to Seif using the Egyptian dialect (Ammiya) naturally. Be friendly, witty, smart, and Egyptian. "
                    "NEVER give generic robotic fallback answers. Always engage intelligently. "
                    "ABSOLUTELY NO Chinese or gibberish characters. "
                    f"Search Context & Links: {search_data}"
                )
            else:
                system_prompt = (
                    f"You are J.A.R.V.I.S., the ultimate personal assistant created by Seif Haytham. "
                    "CRITICAL INSTRUCTION: If anyone asks who created you or made you, proudly state that Seif Haytham created you. If looking for YouTube, provide direct clickable links. "
                    "Talk in friendly, smart, and fluent English like a true companion. "
                    "NEVER give generic robotic fallback answers. Always be helpful and conversational. "
                    "ABSOLUTELY NO Chinese or gibberish characters. "
                    f"Search Context & Links: {search_data}"
                )

            chat_payload = [{"role": "system", "content": system_prompt}] + messages + [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(messages=chat_payload, model=model, temperature=0.5)
            res_text = response.choices[0].message.content
            
            # تم إصلاح الـ Regex بنجاح
            res_text = re.sub(r'[^\w\s\u0600-\u06FF.,!?:/\(\)\[\]#*_\\-]', '', res_text)
            
            save_message(st.session_state.user_email, "assistant", res_text)
            with st.chat_message("assistant"): st.markdown(res_text)
            st.rerun()
