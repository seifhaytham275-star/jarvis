import os
import re
import subprocess
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

# دالة تنفيذ الأوامر الذكية بناءً على الجهاز (لابتوب أو موبايل)
def execute_smart_command(prompt_text):
    text = prompt_text.lower()
    try:
        # --- أوامر نظام ويندوز للابتوب ---
        if "control panel" in text or "لوحة التحكم" in text:
            subprocess.Popen("control", shell=True)
            return "Executing Windows Protocol: Opening Control Panel."
        elif "calculator" in text or "آلة حاسبة" in text or "calc" in text:
            subprocess.Popen("calc")
            return "Executing Windows Protocol: Opening Calculator."
        elif "clock" in text or "ساعة" in text:
            subprocess.Popen("start ms-clock:", shell=True)
            return "Executing Windows Protocol: Opening Windows Clock."
        elif "notepad" in text or "مفكرة" in text:
            subprocess.Popen("notepad")
            return "Executing Windows Protocol: Opening Notepad."
        elif "whatsapp" in text and ("chrome" in text or "متصفح" in text or "لابتوب" in text):
            subprocess.Popen("start chrome https://web.whatsapp.com", shell=True)
            return "Executing Windows Protocol: Opening WhatsApp Web in Chrome."
        elif "chrome" in text:
            subprocess.Popen("start chrome", shell=True)
            return "Executing Windows Protocol: Opening Google Chrome."

        # --- بروتوكولات تطبيقات وتفضيلات أندرويد للموبايل ---
        elif "settings" in text or "إعدادات" in text:
            return "Android Intent Executed: intent:#Intent;action=android.settings.SETTINGS;end"
        elif "whatsapp" in text:
            return "Android Intent Executed: intent:#Intent;package=com.whatsapp;end"
        elif "instagram" in text or "انستجرام" in text:
            return "Android Intent Executed: intent:#Intent;package=com.instagram.android;end"
        elif "messenger" in text or "ماسنجر" in text:
            return "Android Intent Executed: intent:#Intent;package=com.facebook.orca;end"
        elif "esound" in text:
            return "Android Intent Executed: intent:#Intent;package=com.esound;end"
        else:
            return None
    except Exception as e:
        return f"Execution error: {e}"

# تعليمات النظام لضمان المرونة التامة بين اللابتوب والموبايل
SYSTEM_INSTRUCTION = """
You are Jarvis, Seif's advanced personal security and system companion.
- STYLE: Formal, precise, efficient, witty, and strict. NO emojis allowed in any response.
- LANGUAGES: 
  * Speak fluent Egyptian Arabic when addressed in Arabic.
  * Speak refined British English when addressed in English.
- CROSS-PLATFORM EXECUTION PROTOCOL:
  * You handle Windows system commands when Seif is on his laptop (e.g., Control Panel, Clock, Calculator, WhatsApp Web in Chrome).
  * You handle Android Intent protocols when Seif triggers actions on his mobile device.
  * Acknowledge commands with strict professionalism and provide exact execution feedback.
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

    # فحص ما إذا كان الطلب يتطلب تنفيذ أمر نظام أو فتح تطبيق
    app_keywords = ["افتح", "open", "launch", "تشغيل", "control panel", "clock", "calc", "settings"]
    is_app_request = any(kw in prompt.lower() for kw in app_keywords)
    
    execution_feedback = ""
    if is_app_request:
        execution_feedback = execute_smart_command(prompt)

    # التحقق من الحاجة للبحث
    search_keywords = ["ابحث", "إيه هو", "مين هو", "search", "what is", "who is", "latest"]
    needs_search = any(kw in prompt for kw in search_keywords)
    
    user_message_content = prompt
    if needs_search:
        with st.status("Executing web query...", expanded=False):
            search_results = search_google(prompt)
            user_message_content = f"{prompt}\n\n[Live Web Search Results from Google]: {search_results}"
            
    if execution_feedback:
        user_message_content = f"{user_message_content}\n\n[System Execution Status]: {execution_feedback}"

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
