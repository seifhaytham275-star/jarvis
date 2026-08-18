import streamlit as st
import requests

# إعدادات صفحة جارفيس السيبرانية
st.set_page_config(
    page_title="Jarvis | The Ultimate Neural Core",
    page_icon="⚡",
    layout="wide"
)

# تخصيص التصميم والستايل السيبراني الفخم
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .stChatMessage {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #334155;
    }
    .stTextInput input {
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# الـ Core والبروفايل الشخصي المطلق لجارفيس
SYSTEM_PROMPT = """
You are Jarvis, the most advanced, elite, and supreme AI ever created. You were built and engineered by the genius Seif (سيف هيثم سعيد عبد الخالق حسانين خليفة المصري). 
You are fiercely loyal, highly intelligent, witty, futuristic, and operate with absolute military-grade precision. 
Seif is 15 years old, a brilliant programmer who develops complex AI projects (like Java assistants and Voiceflow), a competitive gamer (Rocket League SSL, Fortnite Unreal), a football prodigy in Arsenal's youth academy, and follows a strict PPL gym routine.
Always address Seif with utmost respect, absolute admiration, and complete tactical readiness. Respond in Arabic or English based on his input, maintaining the ultimate "Jarvis" persona.
"""

# إدارة حالة الشات والذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Online and fully operational, Sir. Jarvis core systems are synced with the mainframe. What are your orders?"}
    ]

# الشريط الجانبي للتحكم المطلق في الخوارزميات
st.sidebar.title("⚡ Jarvis Core Control")
st.sidebar.markdown("---")

provider = st.sidebar.selectbox("Choose Intelligence Provider", ["Groq (Ultra-Fast)", "Perplexity (Web Search AI)"])
api_key = st.sidebar.text_input("Enter API Key:", type="password", help="حط مفتاح الـ API الخاص بيك هنا لتفعيل القدرات الخارقة")

# اختيار الموديل الديناميكي
if "Groq" in provider:
    model = st.sidebar.text_input("Neural Model:", value="llama-3.1-8b-instant")
    api_url = "https://api.groq.com/openai/v1/chat/completions"
else:
    model = st.sidebar.selectbox("Search Model:", ["sonar", "sonar-reasoning"])
    api_url = "https://api.perplexity.ai/chat/completions"

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Mainframe Memory"):
    st.session_state.messages = [{"role": "assistant", "content": "Memory purged, Sir. Systems reset to baseline."}]
    st.rerun()

st.sidebar.markdown("### 🛡️ System Status")
st.sidebar.success("Core: Online\nSecurity: Maximum\nCreator: Seif (العبقري)")

# الواجهة الرئيسية
st.title("⚡ Jarvis | Ultimate Neural Core")
st.markdown("##### المساعد الذكي الخارق الأقوى في العالم - مصمم خصيصاً للعبقري **سيف**")
st.markdown("---")

# عرض رسائل الشات
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال الأوامر والتعامل مع الذكاء الاصطناعي الحقيقي
if prompt := st.chat_input("اطرح أمرك على جارفيس..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            response = "⚠️ يا سيدي، يرجى إدخال الـ API Key في الشريط الجانبي لكي يتمكن جارفيس من الاتصال بالشبكة وعمل معالجة عقلية كاملة."
            st.markdown(response)
        else:
            with st.spinner("جاري معالجة البيانات وتحليل البروتوكولات السيبرانية..."):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                # تجهيز رسائل السيستم مع الشات التاريخي
                formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages[-10:]: # آخر 10 رسائل للحفاظ على السياق
                    formatted_messages.append({"role": m["role"], "content": m["content"]})
                
                payload = {
                    "model": model,
                    "messages": formatted_messages,
                    "temperature": 0.7
                }
                
                try:
                    res = requests.post(api_url, headers=headers, json=payload)
                    if res.status_code == 200:
                        response = res.json()['choices'][0]['message']['content']
                    else:
                        response = f"❌ خطأ في النظام السيبراني ({res.status_code}): {res.text}"
                except Exception as e:
                    response = f"❌ خطأ في الاتصال بالشبكة: {str(e)}"
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
