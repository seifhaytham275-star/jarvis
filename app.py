import streamlit as st
import google.generativeai as genai

# إعداد مفتاح جوجل جيميني من إعدادات الأمان
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🤖 Jarvis")

# اختيار موديل جيميني السريع
model = genai.GenerativeModel('gemini-1.5-flash')

# إنشاء وحفظ جلسة المحادثة لمنع أي أخطاء في السجل
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض رسائل الشات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال رسالة جديدة من المستخدم
if prompt := st.chat_input("...اكتب رسالتك هنا"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # إرسال الرسالة لجارفيس واستقبال الرد
    response = st.session_state.chat.send_message(prompt)
    assistant_response = response.text

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
