import streamlit as st
from openai import OpenAI
import requests

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="J.A.R.V.I.S Prime + Search",
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

# 3. إعداد الاتصال بالسيرفر
@st.cache_resource
def get_groq_client(api_key):
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

# 4. دالة البحث عبر Serper
def search_web(query, serper_key):
    url = "https://google.serper.dev/search"
    payload = f'{{"q": "{query}"}}'
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()
        
        # تجميع أول 3 نتائج بحث بشكل مرتب
        snippets = []
        if "organic" in results:
            for item in results["organic"][:3]:
                snippets.append(item.get("snippet", ""))
        return " ".join(snippets)
    except:
        return ""

# 5. الواجهة الرئيسية
st.title("🤖 J.A.R.V.I.S Prime")
st.caption("Integrated with Search & Locked Engine")

# 6. الشريط الجانبي لإدخال المفاتيح
with st.sidebar:
    st.header("⚙️ Control Panel")
    groq_key = st.text_input("Groq API Key", type="password")
    serper_key = st.text_input("Serper API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 🧠 Engine Info")
    TARGET_MODEL = "openai/gpt-oss-120b"
    st.info(f"Locked Model:\n**{TARGET_MODEL}**")

# 7. إدارة الذاكرة (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! J.A.R.V.I.S. at your service—ready with web search."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. صندوق الإرسال والمعالجة
if prompt := st.chat_input("Type your message..."):
    if not groq_key:
        st.error("Please enter your Groq API Key in the sidebar first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # لو المستخدم حط مفتاح Serper، نعمل بحث في الويب الأول
                search_context = ""
                if serper_key:
                    with st.spinner("Searching the web..."):
                        search_results = search_web(prompt, serper_key)
                        if search_results:
                            search_context = f"Web Search Results: {search_results}\n\n"

                # تجهيز رسائل المحادثة مع نتائج البحث إن وجدت
                messages_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                if search_context:
                    # إضافة نتائج البحث لأحدث رسالة عشان الموديل يشوفها
                    messages_payload[-1]["content"] = search_context + "User Question: " + prompt

                client = get_groq_client(groq_key)
                response = client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=messages_payload,
                    temperature=0.7
                )
                
                assistant_response = response.choices[0].message.content
                st.markdown(assistant_response)
                
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
