import os
import streamlit as st
from openai import OpenAI

# ========== إعدادات الصفحة ==========
st.set_page_config(
    page_title="Jarvis AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Jarvis Assistant")
st.caption("Powered by OpenAI GPT-3.5 Turbo")

# ========== جلب المفتاح من Secrets ==========
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("🔒 OPENAI_API_KEY مش موجود في Secrets")
    st.info("روح على Manage app → Secrets وأضف: OPENAI_API_KEY = 'sk-...'")
    st.stop()

# ========== تهيئة OpenAI ==========
try:
    client = OpenAI(api_key=api_key)
    st.success("✅ متصل بـ OpenAI API")
except Exception as e:
    st.error(f"❌ فشل الاتصال بـ OpenAI: {str(e)}")
    st.stop()

# ========== تخزين المحادثة ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== عرض المحادثة السابقة ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ========== إدخال المستخدم ==========
prompt = st.chat_input("اسأل Jarvis أي حاجة...")

if prompt:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # جلب الرد من OpenAI
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"❌ خطأ أثناء جلب الرد: {str(e)}")
