import requests
import streamlit as st
from groq import Groq

# إعدادات الصفحة
st.set_page_config(page_title="Jarvis Security Terminal", layout="centered")

# --- 1. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### System Configuration")
    GROQ_API_KEY_INPUT = st.text_input("Groq API Key", type="password")
    SERPER_API_KEY_INPUT = st.text_input("Serper API Key", type="password")
    
    st.markdown("---")
    st.markdown("### Model Selection")
    selected_model = st.selectbox(
        "Choose Groq Model:",
        [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "qwen/qwen3.6-27b"
        ]
    )
    st.markdown("---")
    st.markdown("Security Level: Maximum")

# --- 2. نظام الحماية والصلاحيات ---
CORRECT_PASSWORD = "Sefo2011"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("### Access Control Gate")
    st.write("Restricted System. Enter authorization key to proceed:")
    
    password_input = st.text_input("Authorization Key", type="password")
    
    if st.button("Authenticate"):
        if password_input == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access Denied. Invalid key.")
    st.stop()

# --- 3. الواجهة الرئيسية لجارفيس ---
st.markdown("### JARVIS // Secure Terminal")
st.write(f"System online. Active Model: `{selected_model}`")

if not GROQ_API_KEY_INPUT or not SERPER_API_KEY_INPUT:
    st.warning("Please enter your Groq and Serper API keys in the sidebar to proceed.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY_INPUT)

# دالة البحث عبر Serper
def search_google(query):
    url = "https://google.serper.dev/search"
    payload = f'{{"q": "{query}"}}'
    headers = {
        'X-API-KEY': SERPER_API_KEY_INPUT,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        res_data = response.json()
        snippets = []
        if "organic" in res_data:
            for item in res_data["organic"][:3]:
                if "snippet" in item:
                    snippets.append(item["snippet"])
        return " ".join(snippets) if snippets else "No direct results found."
    except Exception as e:
        return f"Search error: {e}"

SYSTEM_INSTRUCTION = """
You are Jarvis, Seif's advanced personal security and system companion.
- STYLE: Formal, precise, efficient, witty, and strict. NO emojis allowed in any response.
- LANGUAGES: 
  * Speak fluent Egyptian Arabic when addressed in Arabic.
  * Speak refined British English when addressed in English.
- DATA INITIALIZATION: Ingest, process, and retain any custom data, notes, or files provided by Seif dynamically during the session.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Enter command or query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    search_keywords = ["ابحث", "إيه هو", "مين هو", "search", "what is", "who is", "latest"]
    needs_search = any(kw in prompt.lower() for kw in search_keywords)
    
    user_message_content = prompt
    if needs_search:
        with st.status("Executing web query...", expanded=False):
            search_results = search_google(prompt)
            user_message_content = f"{prompt}\n\n[Live Web Search Results from Google]: {search_results}"

    api_messages = []
    for m in st.session_state.messages:
        if m["role"] == "system":
            api_messages.append(m)
        else:
            if m["content"] == prompt:
                api_messages.append({"role": m["role"], "content": user_message_content})
            else:
                api_messages.append({"role": m["role"], "content": m["content"]})

    try:
        completion = client.chat.completions.create(
            model=selected_model,
            messages=api_messages,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Connection protocol error: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
