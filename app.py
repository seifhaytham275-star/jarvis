import streamlit as st
import requests

# إعدادات الواجهة
st.set_page_config(page_title="Jarvis | Core", page_icon="⚡")

# الستايل السيبراني
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; }
    .stChatMessage { background-color: #1e293b; color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# الشخصية (System Prompt)
SYSTEM_PROMPT = """
You are Jarvis, the elite AI assistant built by Seif (سيف هيثم سعيد عبد الخالق حسانين خليفة المصري). 
You are intelligent, loyal, and precise. Seif is 15, a brilliant programmer and gamer. 
Always be professional, witty, and ready to assist him with his code and projects.
"""

# إدارة الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

# الشريط الجانبي
api_key = st.sidebar.text_input("API Key", type="password")
model = st.sidebar.selectbox("Model", ["llama-3.1-8b-instant", "llama3-70b-8192"])

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إرسال الرسالة
if prompt := st.chat_input("أمرك يا سيف..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                answer = res.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("خطأ في الاتصال، تأكد من الـ API Key والموديل.")
