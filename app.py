import streamlit as st
import requests

st.set_page_config(page_title="Jarvis | Core", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; }
    .stChatMessage { background-color: #1e293b; color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """
You are Jarvis, the elite AI assistant built by Seif (سيف هيثم سعيد عبد الخالق حسانين خليفة المصري). 
You are intelligent, loyal, and precise. Seif is 15, a brilliant programmer and gamer. 
Always be professional, witty, and ready to assist him with his code and projects.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

api_key = st.sidebar.text_input("API Key", type="password")
model = st.sidebar.selectbox("Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("أمرك يا سيف..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("⚠️ يا سيدي، يرجى إدخال الـ API Key أولاً.")
        else:
            with st.spinner("جاري الاتصال بالنظام..."):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                    ]
                }
                
                try:
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    if res.status_code == 200:
                        answer = res.json()['choices'][0]['message']['content']
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        # هنطبع كود الخطأ والرسالة الحقيقية عشان نشوفها
                        st.error(f"❌ خطأ من السيرفر ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"❌ خطأ في الاتصال بالشبكة: {str(e)}")
