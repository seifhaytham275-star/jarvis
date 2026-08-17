import streamlit as st
from groq import Groq
import sqlite3

# --- إعدادات الحماية (الباسورد) ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        pwd = st.text_input("أدخل كلمة المرور:", type="password")
        if st.button("دخول"):
            if pwd == st.secrets.get("APP_PASSWORD"):
                st.session_state.authenticated = True
                st.rerun()
        return False
    return True

if check_password():
    # --- دالة إدارة قاعدة البيانات ---
    def init_db():
        conn = sqlite3.connect('jarvis_sessions.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, name TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS messages (session_id INTEGER, role TEXT, content TEXT)')
        conn.commit()
        return conn

    conn = init_db()
    c = conn.cursor()

    # --- القائمة الجانبية (إدارة الشاتات) ---
    st.sidebar.title("📁 جلسات جارفيس")
    
    # إنشاء شات جديد
    if st.sidebar.button("+ شات جديد"):
        c.execute("INSERT INTO sessions (name) VALUES (?)", ("شات جديد",))
        conn.commit()
    
    # عرض الشاتات
    sessions = c.execute("SELECT * FROM sessions").fetchall()
    selected_session = st.sidebar.radio("اختر جلسة:", [s[1] for s in sessions], index=0)
    
    # جلب الـ ID للجلسة المختارة
    current_session_id = c.execute("SELECT id FROM sessions WHERE name=?", (selected_session,)).fetchone()[0]

    # إعادة تسمية الشات
    new_name = st.sidebar.text_input("غير اسم الشات الحالي:")
    if st.sidebar.button("تحديث الاسم"):
        c.execute("UPDATE sessions SET name=? WHERE id=?", (new_name, current_session_id))
        conn.commit()
        st.rerun()

    # --- الشاشة الرئيسية ---
    st.title(f"مرحباً سيف - {selected_session}")
    
    # عرض الرسائل الخاصة بالجلسة المختارة
    msgs = c.execute("SELECT role, content FROM messages WHERE session_id=?", (current_session_id,)).fetchall()
    for r, c_text in msgs:
        with st.chat_message(r): st.markdown(c_text)

    # استقبال الرد
    if prompt := st.chat_input("تفضل يا سيف..."):
        c.execute("INSERT INTO messages VALUES (?, ?, ?)", (current_session_id, "user", prompt))
        
        # استدعاء النموذج (مع الحفاظ على الخصوصية)
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        c.execute("INSERT INTO messages VALUES (?, ?, ?)", (current_session_id, "assistant", response))
        conn.commit()
        st.rerun()

    conn.close()
