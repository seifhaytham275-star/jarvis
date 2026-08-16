import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import sqlite3
import re
import requests

# --- إعدادات الصفحة ---
st.set_page_config(page_title="J.A.R.V.I.S. Global Omni-Core", page_icon="⚡", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #030303; color: #00ffcc; }
    .stButton>button { border: 1px solid #00ffcc; color: #00ffcc; background-color: transparent; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #00ffcc; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- تهيئة قواعد البيانات ---
def init_db():
    conn = sqlite3.connect('jarvis_global_core.db')
    conn.execute('CREATE TABLE IF NOT EXISTS messages (email TEXT, role TEXT, content TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (email TEXT, task TEXT, category TEXT, status INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS notes (email TEXT, title TEXT, content TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- التعرف التلقائي على المستخدم ---
def get_user_profile(email):
    email_lower = email.strip().lower()
    if "seif_haytham" in email_lower:
        return "سيف هيثم"
    name_part = email_lower.split('@')[0]
    clean_name = re.sub(r'\d+', '', name_part)
    return clean_name.replace('.', ' ').replace('_', ' ').title()

# --- شاشة تسجيل الدخول ---
if "user_email" not in st.session_state:
    st.title("🔐 J.A.R.V.I.S. Global Access Core")
    email_input = st.text_input("البريد الإلكتروني (Gmail):")
    groq_key = st.text_input("Groq API Key:", type="password")
    serper_key = st.text_input("Serper API Key (اختياري للبحث):", type="password")
    
    if st.button("تشغيل النظام العالمي"):
        if email_input and groq_key:
            st.session_state.user_email = email_input.strip().lower()
            st.session_state.user_name = get_user_profile(email_input)
            st.session_state.groq_key = groq_key
            st.session_state.serper_key = serper_key
            st.rerun()
        else:
            st.error("برجاء إدخال البريد الإلكتروني ومفتاح الـ Groq API!")
    st.stop()

user_name = st.session_state.user_name
user_email = st.session_state.user_email

# --- القائمة الجانبية وإعدادات اللغات العالمية والنماذج ---
st.sidebar.title(f"⚡ لوحة تحكم جارفيس")
st.sidebar.info(f"المستخدم: **{user_name}** 🦾")

persona_mode = st.sidebar.selectbox("شخصية جارفيس:", [
    "وضع جارفيس الخارق (صديق ومبدع - لهجة مصرية)",
    "طوني ستارك (ساخر وعبقري)",
    "مطور برمجيات محترف"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🌍 لغة التطبيق العالمية (Google Play Ready)")
app_language = st.sidebar.selectbox("اختر لغة جارفيس:", [
    "العربية (Arabic)",
    "الإنجليزية (English)",
    "الألمانية (Deutsch)",
    "الصينية (中文 - Chinese)",
    "البرتغالية (Português)",
    "الفرنسية (Français)",
    "الإسبانية (Español)",
    "اليابانية (日本語 - Japanese)",
    "الروسية (Русский)",
    "الإيطالية (Italiano)"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🧠 اختيار النموذج والسرعة")
model_choice = st.sidebar.selectbox("النموذج الذكي:", [
    "llama-3.3-70b-versatile (العملاق - ذكاء فائق)",
    "llama-3.2-90b-vision-preview (متعدد الوسائط - رؤية ونص)",
    "llama-3.1-8b-instant (السريع جداً - توكنز أقل)",
    "llama-3.2-3b-preview (خفيف واقتصادي للتوكنز)"
])
selected_model = model_choice.split(" ")[0]

if st.sidebar.button("قفل النظام (تسجيل خروج)"):
    st.session_state.clear()
    st.rerun()

# --- محرك البحث ---
def search_web(query):
    if not st.session_state.get("serper_key"): return ""
    try:
        url = "https://google.serper.dev/search"
        headers = {'X-API-KEY': st.session_state.serper_key, 'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, json={"q": query}).json()
        return "\n".join([f"{i.get('title')}: {i.get('link')}" for i in res.get("organic", [])[:3]])
    except: return ""

st.title(f"🤖 J.A.R.V.I.S. Global Omni-Core - أهلاً بك يا {user_name}")

# --- الـ 6 تبويبات الشاملة ---
tabs = st.tabs([
    "💬 المحادثة والصوت", 
    "⚽ صانع الألعاب والمواقع", 
    "📸 المعرض (فيديو وصور)", 
    "📓 نوت بوك الذكي", 
    "🏋️‍♂️ الجيم والمذاكرة", 
    "🔗 التطبيقات والواتساب"
])

# 1. المحادثة والصوت
with tabs[0]:
    st.subheader("💬 العقل العصبي والصوت المباشر")
    
    voice_script = f"""
    <div style="background:#111; padding:15px; border-radius:10px; border:1px solid #00ffcc; margin-bottom:15px;">
        <p style="color:#00ffcc; margin:0 0 10px 0;">🎙️ الأوامر الصوتية:</p>
        <button onclick="startListening()" style="background-color:#00ffcc; color:black; padding:8px 15px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">تحدث إلى جارفيس</button>
        <p id="transcript" style="color:white; margin-top:8px;"></p>
    </div>
    <script>
    function startListening() {{
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'ar-EG';
        recognition.onresult = function(event) {{
            const text = event.results[0][0].transcript;
            document.getElementById('transcript').innerText = "قلت: " + text;
            const speech = new SpeechSynthesisUtterance("أهلاً بك يا {user_name}، سمعتك تقول: " + text);
            speech.lang = 'ar-EG';
            window.speechSynthesis.speak(speech);
        }};
        recognition.start();
    }
    </script>
    """
    components.html(voice_script, height=130)

    conn = sqlite3.connect('jarvis_global_core.db')
    msgs = conn.execute("SELECT role, content FROM messages WHERE email=?", (user_email,)).fetchall()
    conn.close()

    for r, c in msgs:
        with st.chat_message(r):
            st.markdown(c)

    prompt = st.chat_input(f"أؤمرني يا {user_name.split()[0]}...")
    if prompt:
        conn = sqlite3.connect('jarvis_global_core.db')
        conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_email, "user", prompt))
        conn.commit()
        conn.close()

        client = Groq(api_key=st.session_state.groq_key)
        web_ctx = search_web(prompt)
        sys_prompt = f"""
        You are JARVIS, an advanced AI assistant.
        User: {user_name}.
        Persona: {persona_mode}.
        Target Language: {app_language}. Always reply in this selected language, adapting to users from anywhere in the world.
        Web Context: {web_ctx}
        """

        with st.spinner(f"جاري المعالجة باللغة المختارة وبالنموذج ({selected_model})..."):
            try:
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
                    model=selected_model
                ).choices[0].message.content

                conn = sqlite3.connect('jarvis_global_core.db')
                conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_email, "assistant", res))
                conn.commit()
                conn.close()
                st.markdown(res)
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# 2. صانع الألعاب والمواقع (مثل لعبة الدوري المصري)
with tabs[1]:
    st.subheader("⚽ صانع الألعاب والمواقع الخارق (Game & Web Creator)")
    st.markdown("اطلب من جارفيس يبني لك موقع أو لعبة (مثل لعبة كرة قدم للدوري المصري بالأندية الحقيقية):")
    
    app_request = st.text_area("صف المشروع أو اللعبة:", "انشئ لي لعبة كرة قدم خفيفة بجرافيكس جميل تضم أندية الدوري المصري (الأهلي، الزمالك، بيراميدز، الإسماعيلي) تعمل مباشرة داخل المتصفح.")
    
    if st.button("🚀 توليد وتشغيل المشروع برمجياً"):
        client = Groq(api_key=st.session_state.groq_key)
        code_prompt = f"""
        You are an elite game and web developer. Write a complete, standalone, beautiful HTML file including CSS and JavaScript for the following request: {app_request}.
        Make sure it is fully functional, interactive, and beautifully styled. Return ONLY the raw HTML code inside a ```html block.
        """
        with st.spinner("جاري كتابة وبرمجة اللعبة أو الموقع..."):
            gen_res = client.chat.completions.create(
                messages=[{"role": "user", "content": code_prompt}],
                model=selected_model
            ).choices[0].message.content
            
            match = re.search(r'```html(.*?)```', gen_res, re.DOTALL)
            html_code = match.group(1) if match else gen_res
            
            st.success("تم بناء المشروع بنجاح!")
            st.markdown("### معاينة تفاعلية داخل التطبيق:")
            components.html(html_code, height=500, scrolling=True)

# 3. المعرض (صور وفيديوهات)
with tabs[2]:
    st.subheader("📸 معرض الوسائط الذكي (Gallery & Media)")
    uploaded_files = st.file_uploader("ارفع الصور أو الفيديوهات هنا:", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'mov'])
    if uploaded_files:
        for file in uploaded_files:
            st.write(f"📁 اسم الملف: {file.name}")
            if file.type.startswith("image"):
                st.image(file, caption=file.name, use_container_width=True)
            elif file.type.startswith("video"):
                st.video(file)

# 4. نوت بوك الذكي (NotebookLM Style)
with tabs[3]:
    st.subheader("📓 نوت بوك الأبطال (Smart Notebook)")
    n_title = st.text_input("عنوان الملاحظة / الملخص:")
    n_content = st.text_area("محتوى الملاحظة أو النص المراد تخزينه وتحليله:")
    if st.button("حفظ في النوت بوك"):
        conn = sqlite3.connect('jarvis_global_core.db')
        conn.execute("INSERT INTO notes VALUES (?, ?, ?)", (user_email, n_title, n_content))
        conn.commit()
        conn.close()
        st.success("تم الحفظ في الذاكرة بنجاح!")
    
    st.markdown("### 📚 ملاحظاتك المخزنة:")
    conn = sqlite3.connect('jarvis_global_core.db')
    notes = conn.execute("SELECT title, content FROM notes WHERE email=?", (user_email,)).fetchall()
    conn.close()
    for title, content in notes:
        with st.expander(f"📌 {title}"):
            st.write(content)

# 5. الجيم والمذاكرة
with tabs[4]:
    st.subheader("🏋️‍♂️ ميزان الجيم والدراسة (البكالوريا المتكاملة)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### جدول التمارين (Push/Pull/Legs)")
        workout = st.selectbox("التمرين اليوم:", ["Push (دفع)", "Pull (سحب)", "Legs (أرجل)", "Calisthenics (سيندي)"])
        if st.button("تسجيل التمرين 💪"):
            st.success(f"تم تسجيل تمرين {workout} بنجاح يا بطل!")
    with col2:
        st.markdown("### مهام المذاكرة والدراسة")
        task_name = st.text_input("المهمة الدراسية الجديدة:")
        if st.button("إضافة للمهام"):
            conn = sqlite3.connect('jarvis_global_core.db')
            conn.execute("INSERT INTO tasks VALUES (?, ?, 'دراسة', 0)", (user_email, task_name))
            conn.commit()
            conn.close()
            st.success("تمت الإضافة للمخطط الدراسي!")

# 6. التطبيقات والواتساب
with tabs[5]:
    st.subheader("🔗 مركز التطبيقات والروابط الذكية")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ فتح يوتيوب فوراً"):
            components.html("""<script>window.open('[https://www.youtube.com](https://www.youtube.com)', '_blank');</script>""", height=0)
        if st.button("📸 فتح إنستجرام فوراً"):
            components.html("""<script>window.open('[https://www.instagram.com](https://www.instagram.com)', '_blank');</script>""", height=0)
    with c2:
        wa_text = st.text_input("رسالة واتساب المراد إرسالها:")
        if wa_text:
            safe_url = f"[https://wa.me/?text=](https://wa.me/?text=){requests.utils.quote(wa_text)}"
            st.link_button("🚀 إرسال عبر واتساب (تأكيد يدوي)", safe_url)
