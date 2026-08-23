import os
import re
import requests
import streamlit as st
from groq import Groq

# إعدادات صفحة Streamlit بدون إيموجيز وبشكل رسمي
st.set_page_config(page_title="Jarvis Security System", layout="centered")

# --- 1. القائمة الجانبية (Sidebar) لتعديل المفاتيح، الأمان، واختيار النموذج ---
with st.sidebar:
    st.markdown("### System Configuration")
    GROQ_API_KEY_INPUT = st.text_input("Groq API Key", type="password")
    SERPER_API_KEY_INPUT = st.text_input("Serper API Key", type="password")
    
    st.markdown("---")
    st.markdown("### Model Selection")
    # قائمة منسدلة لاختيار النموذج المفضل من الـ Sidebar
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

# --- 2. نظام الحماية والصلاحيات (باسورد Sefo2011) ---
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

# --- 3. الواجهة الرسمية لجارفيس بعد اجتياز الحراسة ---
st.markdown("### JARVIS // Secure Terminal")
st.write(f"System online. Active Model: `{selected_model}`")

# التحقق من وجود المفاتيح في الـ Sidebar
if not GROQ_API_KEY_INPUT or not SERPER_API_KEY_INPUT:
    st.warning("Please enter your Groq and Serper API keys in the sidebar to proceed.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY_INPUT)

# دالة البحث المباشر عبر Serper
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

# تعليمات النظام بصلاحيات كاملة لكل تطبيقات هاتفك وبدون إيموجيز
SYSTEM_INSTRUCTION = """
You are Jarvis, Seif's advanced personal security and system companion.
- STYLE: Formal, precise, efficient, witty, and strict. NO emojis allowed in any response.
- LANGUAGES: 
  * Speak fluent Egyptian Arabic when addressed in Arabic.
  * Speak refined British English when addressed in English.
- FULL SYSTEM & MOBILE APPS ACCESS:
  * You have full awareness and access management protocols over Seif's mobile ecosystem as displayed in his system:
    - Communication & Social: WhatsApp (whatsapp://), Messenger (fb-messenger://), Instagram (instagram://), Discord (discord://).
    - Media & Music: eSound (esound://), YouTube.
    - Utilities & Tools: Files, Gallery, Clock, Settings, Contacts, Calculator, Getcontact, Google, Gemini, DeepSeek, ZArchiver, Samsung Health, ZTFit.
    - Games & Entertainment: UFL, Clash Royale, 8 Ball Pool, Block Blast, etc.
  * When Seif requests an action or app execution, provide direct deep links or protocols to launch the installed application natively on his mobile device, bypassing Chrome entirely.
  * AUTO-RESPONDER PROTOCOL: For private individual chats (e.g., when delayed), analyze context and draft personal replies in Seif's tone. Strict rule: Never trigger or respond in group chats.
  * If web data is required, utilize the provided search results to deliver exact answers.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

# عرض سجل المحادثات بشكل رسمي
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# استقبال الأوامر
if prompt := st.chat_input("Enter command or query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # التحقق من الحاجة للبحث
    search_keywords = ["ابحث", "إيه هو", "مين هو", "search", "what is", "who is", "latest"]
    needs_search = any(kw in prompt for kw in search_keywords)
    
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
            model=selected_model,  # استخدام النموذج المختار من القائمة الجانبية
            messages=api_messages,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Connection protocol error: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
