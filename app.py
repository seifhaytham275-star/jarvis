import streamlit as st
from openai import OpenAI

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="J.A.R.V.I.S Prime",
    page_icon="🤖",
    layout="centered"
)

# 2. تنسيقات CSS لشكل مظلم وأنيق
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput input {
        background-color: #161b22;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. العنوان الرئيسي
st.title("🤖 J.A.R.V.I.S Prime")
st.caption("Advanced AI Assistant - Production Ready")

# 4. الشريط الجانبي لإدخال مفتاح الـ API
with st.sidebar:
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 🧠 Engine Info")
    # تثبيت الموديل بشكل دائم كما طلبته
    TARGET_MODEL = "openai/gpt-oss-120b"
    st.info(f"Locked Model:\n**{TARGET_MODEL}**")

# 5. إدارة الذاكرة (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! J.A.R.V.I.S. at your service—ready to assist."}
    ]

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. صندوق إدخال الرسائل والاتصال بالموديل
if prompt := st.chat_input("Type your message..."):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar first!")
    else:
        # إضافة رسالة المستخدم للذاكرة
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # توليد رد الذكاء الاصطناعي
        with st.chat_message("assistant"):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                
                response = client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.7
                )
                
                assistant_response = response.choices[0].message.content
                st.markdown(assistant_response)
                
                # حفظ رد المساعد في الذاكرة
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
