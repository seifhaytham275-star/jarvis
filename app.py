import datetime
import os
import webbrowser
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Pro", page_icon="🤖", layout="centered"
)

st.title("🤖 Jarvis Ultimate Pro - ChatBox")
st.write("All systems operational, Sir. Type your command below.")

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
  st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# استقبال مدخلات المستخدم عبر شات Streamlit
if query := st.chat_input("How can I help you today, Sir?"):
  # عرض رسالة المستخدم
  st.chat_message("user").markdown(query)
  st.session_state.messages.append({"role": "user", "content": query})

  # معالجة الأوامر
  query_lower = query.lower()

  if "open youtube" in query_lower or "يوتيوب" in query_lower:
    response = "Opening YouTube, Sir."
    webbrowser.open("https://www.youtube.com")

  elif "open google" in query_lower or "جوجل" in query_lower:
    response = "Opening Google, Sir."
    webbrowser.open("https://www.google.com")

  elif "open tiktok" in query_lower or "تيك توك" in query_lower:
    response = "Opening TikTok, Sir."
    webbrowser.open("https://www.tiktok.com")

  elif "open calculator" in query_lower or "حاسبة" in query_lower:
    response = "Opening Calculator, Sir."
    try:
      os.system("calc")
    except:
      pass

  elif "open notepad" in query_lower or "نوت باد" in query_lower:
    response = "Opening Notepad, Sir."
    try:
      os.system("notepad")
    except:
      pass

  elif "time" in query_lower or "الوقت" in query_lower:
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    response = f"Sir, the time is {str_time}"

  elif "hello" in query_lower or "hi" in query_lower:
    response = (
        "Jarvis Ultimate Pro ChatBox is online. All systems operational, Sir."
    )

  else:
    response = f"Command '{query}' processed successfully, Sir."

  # عرض رد جارفيس
  with st.chat_message("assistant"):
    st.markdown(response)
  st.session_state.messages.append({"role": "assistant", "content": response})
