import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Stark", page_icon="⚡", layout="centered"
)

st.title("⚡ Jarvis Ultimate Stark (Multi-Server Protocol)")
st.write(
    "System Status: Online | Auto-Failover Search Active (100% Free, No API"
    " Key)"
)

# تهيئة سجل المحادثة والمهام
if "messages" not in st.session_state:
  st.session_state.messages = []

if "tasks" not in st.session_state:
  st.session_state.tasks = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# استقبال مدخلات المستخدم بالعامية أو الإنجليزية
if query := st.chat_input("كلمني بالعامية المصرية أو الإنجليزية يا سيدي..."):
  st.chat_message("user").markdown(query)
  st.session_state.messages.append({"role": "user", "content": query})

  query_lower = query.lower()
  response = ""

  is_english = any(ord(char) < 128 and char.isalpha() for char in query) and not any(
      ar_word in query for ar_word in ["فين", "إيه", "كام", "الساعة", "ازيك", "عايز", "ايه", "الجو", "ليه"]
  )

  # 1. الوقت والتاريخ
  if "time" in query_lower or "الساعة" in query_lower or "الوقت" in query_lower:
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    if is_english:
      response = f"The time is {str_time}, Sir. Time flies when you're building the future."
    else:
      response = f"الساعة دلوقتي يا سيدي {str_time}، الوقت بيعدي وإحنا بنبتكر."

  # 2. إدارة المهام وتنظيم الحياة
  elif "مهمة" in query_lower or "task" in query_lower or "اضف" in query_lower or "add" in query_lower:
    clean_task = (
        query.replace("مهمة", "")
        .replace("task", "")
        .replace("اضف", "")
        .replace("add", "")
        .strip()
    )
    if clean_task:
      st.session_state.tasks.append(clean_task)
      if is_english:
        response = f"Task '{clean_task}' added, Sir. No room for laziness in Stark Tower."
      else:
        response = f"تم تسجيل المهمة ('{clean_task}') يا بطل. مفيش مكان للكسل في برج ستارك!"
    else:
      response = "حدد المهمة بوضوح يا سيدي عشان أسجلها."

  elif "مهامي" in query_lower or "tasks" in query_lower:
    if not st.session_state.tasks:
      response = (
          "قائمتك فاضية خالص يا سيدي. عايشها فري ولا ناسي شغلك؟"
          if not is_english
          else "Your task list is completely empty, Sir. Living life freely or just forgetting?"
      )
    else:
      tasks_list = "\n".join([f"- {t}" for t in st.session_state.tasks])
      response = (
          f"دي مهامك الحالية يا سيدي:\n{tasks_list}"
          if not is_english
          else f"Here are your current tasks, Sir:\n{tasks_list}"
      )

  # 3. البحث الذكي مع تدوير السيرفرات (Multi-Server Fallback)
  else:
    search_servers = [
        "https://searx.be/search",
        "https://searx.tiekoetter.com/search",
        "https://search.ononoki.org/search",
    ]
    
    success = False
    results = []

    for server in search_servers:
      try:
        params = {
            "q": query,
            "format": "json",
            "language": "en" if is_english else "ar",
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(server, params=params, headers=headers, timeout=3)
        if res.status_code == 200 and "application/json" in res.headers.get("Content-Type", ""):
          data = res.json()
          results = data.get("results", [])
          if results:
            success = True
            break
      except:
        continue

    if success and results:
      snippets = "\n\n".join(
          [
              f"• **{r.get('title', 'بدون عنوان')}**\n{r.get('content', '')}"
              for r in results[:2]
          ]
      )
      response = (
          f"**[Stark Secure Search]:**\n\n{snippets}\n\n*النتائج قدامك يا سيدي بدقة تامة وبدون لف ودوران.*"
          if not is_english
          else f"**[Stark Secure Search]:**\n\n{snippets}\n\n*Here are the precise results, Sir.*"
      )
    else:
      response = (
          "جرت محاولة عبر جميع السيرفرات الحرة ولكنها مضغوطة حالياً يا سيدي، أنظمتنا تعمل بامتياز، جرب سؤالاً آخر."
          if not is_english
          else "All free servers are busy right now, Sir, but our internal systems are fully operational."
      )

  # عرض رد جارفيس
  with st.chat_message("assistant"):
    st.markdown(response)
  st.session_state.messages.append({"role": "assistant", "content": response})

# شريط جانبي لإدارة المهام السريعة
with st.sidebar:
  st.subheader("📋 مهام توني ستارك / Stark Tasks")
  if st.session_state.tasks:
    for idx, t in enumerate(st.session_state.tasks, 1):
      st.write(f"{idx}. {t}")
  else:
    st.write("مفيش مهام حالياً / No tasks currently.")
