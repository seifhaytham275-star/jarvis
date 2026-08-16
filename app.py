import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import sqlite3
import re
import requests

# --- إعدادات الصفحة والتصميم المستقبلي ---
st.set_page_config(page_title="J.A.R.V.I.S. Ultimate 50x", page_icon="⚡", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .stButton>button { border: 1px solid #00f2ff; color: #00f2ff; background-color: transparent; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #00f2ff; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- تهيئة قواعد البيانات ---
def init_db():
    conn = sqlite3.connect('jarvis_ultimate_core.db')
    conn.execute('CREATE TABLE IF NOT EXISTS messages (email TEXT, role TEXT, content TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (email TEXT, task TEXT, category TEXT, status INTEGER)')
    conn.commit()
    conn.close()

init_db()

# --- التعرف التلقائي على المستخدم من الإيميل (بدون أرقام) ---
def get_user_profile(email):
    email_lower = email.strip().lower()
    if "seif_haytham" in email_lower:
        return "سيف هيثم"
    name_part = email_lower.split('@')[0]
    clean_name = re.sub(r'\d+', '', name_part)
    return clean_name.replace('.', ' ').replace('_', ' ').title()

# --- شاشة تسجيل الدخول ---
if "user_email" not in st.session_state:
    st.title("🔐 J.A.R.V.I.S. Neural Access Core")
    st.markdown("### أدخل بريدك الإلكتروني ومفتاح الـ Groq API للبدء يا بطل:")
    email_input = st.text_input("البريد الإلكتروني (Gmail):")
    groq_key = st.text_input("Groq API Key:", type="password")
    serper_key = st.text_input("Serper API Key (اختياري للبحث):", type="password")
    
    if st.button("تفعيل النظام الخارق"):
        if email_input and groq_key:
            st.session_state.user_email = email_input.strip().lower()
            st.session_state.user_name = get_user_profile(email_input)
            st.session_state.groq_key = groq_key
            st.session_state.serper_key = serper_key
            st.rerun()
        else:
            st.error("برجاء إدخال البريد ومفتاح الـ API!")
    st.stop()

user_name = st.session_state.user_name
user_email = st.session_state.user_email

st.sidebar.title(f"⚡ لوحة تحكم جارفيس")
st.sidebar.info(f"المستخدم الحالي: **{user_name}** 🦾")

if st.sidebar.button("قفل النظام (تسجيل خروج)"):
    st.session_state.clear()
    st.rerun()

st.sidebar.subheader("🎨 إعدادات الشخصية واللغة")
persona_mode = st.sidebar.selectbox("اختر وضع الذكاء:", [
    "وضع جارفيس الخارق (صديق ومبدع - لهجة مصرية وسلسة)",
    "طوني ستارك (ساخر وعبقري)",
    "رسمي واحترافي"
])
model_choice = st.sidebar.selectbox("النموذج:", ["llama-3.3-70b-versatile", "llama-3.2-90b-vision-preview"])

def search_web(query):
    if not st.session_state.get("serper_key"): return ""
    try:
        url = "https://google.serper.dev/search"
        headers = {'X-API-KEY': st.session_state.serper_key, 'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, json={"q": query}).json()
        return "\n".join([f"{i.get('title')}: {i.get('link')}" for i in res.get("organic", [])[:3]])
    except: return ""

st.title(f"🤖 J.A.R.V.I.S. Neural Core - أهلاً بك يا {user_name}")

tabs = st.tabs([
    "💬 المحادثة الذكية والصوت", 
    "🏋️‍♂️ الجيم وصحة البطل", 
    "📚 المذاكرة والإنتاجية", 
    "🔗 التطبيقات والروابط والواتساب", 
    "🛠️ الأدوات المتقدمة"
])

# 1. تبويب المحادثة الذكية والصوت
with tabs[0]:
    st.subheader("💬 العقل المركزي والنظام الصوتي")
    
    voice_script = """
    <div style="background:#111; padding:15px; border-radius:10px; border:1px solid #00f2ff; margin-bottom:15px;">
        <p style="color:#00f2ff; margin:0 0 10px 0;">🎙️ تحكم صوتي مباشر:</p>
        <button onclick="startListening()" style="background-color:#00f2ff; color:black; padding:8px 15px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">تحدث إلى جارفيس</button>
        <p id="transcript" style="color:white; margin-top:8px;"></p>
    </div>
    <script>
    function startListening() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'ar-EG';
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            document.getElementById('transcript').innerText = "قلت: " + text;
            speakText("أهلاً بك يا بطل، سمعتك تقول: " + text);
        };
        recognition.start();
    }
    function speakText(text) {
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = 'ar-EG';
        speech.rate = 1.0;
        window.speechSynthesis.speak(speech);
    }
    </script>
    """
    components.html(voice_script, height=130)

    conn = sqlite3.connect('jarvis_ultimate_core.db')
    msgs = conn.execute("SELECT role, content FROM messages WHERE email=?", (user_email,)).fetchall()
    conn.close()

    for r, c in msgs:
        with st.chat_message(r):
            st.markdown(c)

    prompt = st.chat_input(f"تفضل يا {user_name.split()[0]}, أنا في خدمتك...")
    if prompt:
        conn = sqlite3.connect('jarvis_ultimate_core.db')
        conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_email, "user", prompt))
        conn.commit()
        conn.close()

        client = Groq(api_key=st.session_state.groq_key)
        web_ctx = search_web(prompt)

        system_prompt = f"""
        You are J.A.R.V.I.S., an advanced AI assistant.
        The current user interacting with you is: {user_name}.
        Always address the user by their exact name: {user_name}.
        Persona: {persona_mode}.
        Web Context: {web_ctx}
        """

        with st.spinner("جاري المعالجة العصبية..."):
            try:
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                    model=model_choice
                )
                res_text = res.choices[0].message.content
                
                conn = sqlite3.connect('jarvis_ultimate_core.db')
                conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_email, "assistant", res_text))
                conn.commit()
                conn.close()

                st.markdown(res_text)
                st.rerun()
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")

# 2. تبويب الجيم والصحة
with tabs[1]:
    st.subheader("🏋️‍♂️ مركز لياقة وصحة البطل")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("### سجل التمارين اليومية")
        workout_type = st.selectbox("نوع التمرين:", ["Push (دفع)", "Pull (سحب)", "Legs (أرجل)", "Calisthenics (سيندي)"])
        if st.button("تسجيل التمرين"):
            st.success(f"تم تسجيل تمرين {workout_type} بنجاح يا بطل! استمر 💪")
        
        water_count = st.number_input("أكواب المياه اليومية:", 0, 15, 4)
        if st.button("تحديث المياه"):
            st.info(f"عاش يا {user_name.split()[0]}! جسمك محتاج مياه للاستشفاء العضلي.")

    with col_g2:
        st.markdown("### حاسبة كتلة الجسم (BMI)")
        weight = st.number_input("الوزن (كجم):", 30.0, 150.0, 65.0)
        height = st.number_input("الطول (سم):", 100.0, 220.0, 175.0)
        if st.button("حساب الـ BMI"):
            bmi = weight / ((height / 100) ** 2)
            st.metric("مؤشر كتلة الجسم", f"{bmi:.1f}")

# 3. تبويب المذاكرة والإنتاجية
with tabs[2]:
    st.subheader("📚 الإنتاجية وميزان المذاكرة والجيم")
    st.markdown("نظم وقتك بين دراستك (نظام البكالوريا المتكامل) وبين تمرينك بكل سهولة:")
    
    new_t = st.text_input("أضف مهمة جديدة:")
    t_cat = st.selectbox("التصنيف:", ["دراسة", "جيم", "مشروع برمجيات", "أخرى"])
    if st.button("إضافة للمهام"):
        if new_t:
            conn = sqlite3.connect('jarvis_ultimate_core.db')
            conn.execute("INSERT INTO tasks VALUES (?, ?, ?, 0)", (user_email, new_t, t_cat))
            conn.commit()
            conn.close()
            st.success("تمت الإضافة للمخطط!")

    st.markdown("### 📋 مهامك الحالية:")
    conn = sqlite3.connect('jarvis_ultimate_core.db')
    user_tasks = conn.execute("SELECT rowid, task, category FROM tasks WHERE email=? AND status=0", (user_email,)).fetchall()
    conn.close()

    for tid, tsk, cat in user_tasks:
        cols = st.columns([4, 1])
        cols.markdown(f"**[{cat}]** {tsk}")
        if cols.button("إنجاز ✅", key=f"tsk_{tid}"):
            conn = sqlite3.connect('jarvis_ultimate_core.db')
            conn.execute("UPDATE tasks SET status=1 WHERE rowid=?", (tid,))
            conn.commit()
            conn.close()
            st.rerun()

# 4. تبويب التطبيقات والروابط والواتساب الآمن
with tabs[3]:
    st.subheader("🔗 مركز التطبيقات والروابط الذكية")
    
    col_app1, col_app2 = st.columns(2)
    with col_app1:
        if st.button("▶️ فتح يوتيوب فوراً"):
            components.html("""<script>window.open('https://www.youtube.com', '_blank');</script>""", height=0)
            st.success("تم فتح يوتيوب!")
        
        if st.button("📸 فتح إنستجرام فوراً"):
            components.html("""<script>window.open('https://www.instagram.com', '_blank');</script>""", height=0)
            st.success("تم فتح إنستجرام!")

    with col_app2:
        st.markdown("### 💬 إرسال واتساب آمن (تأكيد يدوي)")
        wa_msg = st.text_input("اكتب الرسالة المراد إرسالها:")
        if wa_msg:
            safe_url = f"https://wa.me/?text={requests.utils.quote(wa_msg)}"
            st.link_button("🚀 اضغط هنا لتأكيد الإرسال عبر واتساب", safe_url)

# 5. تبويب الأدوات المتقدمة
with tabs[4]:
    st.subheader("🛠️ أدوات جارفيس المتقدمة")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("### 🧮 حاسبة علمية")
        expr = st.text_input("أدخل المعادلة الرياضية (مثال: 50 * 2 + 10):")
        if st.button("احسب"):
            try:
                ans = eval(expr)
                st.success(f"النتيجة: {ans}")
            except Exception as e:
                st.error(f"خطأ: {e}")

    with col_t2:
        st.markdown("### 🌐 مترجم لغات العالم")
        text_to_trans = st.text_input("النص المراد ترجمته:")
        target_lang = st.selectbox("اللغة المستهدفة:", ["الإنجليزية", "العربية", "الفرنسية", "الألمانية", "الإسبانية"])
        if st.button("ترجم الآن"):
            st.info(f"جارفيس يقوم بالترجمة إلى {target_lang}...")
