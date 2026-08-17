import datetime
from bs4 import BeautifulSoup
import requests
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Stark - God Mode",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ Jarvis Ultimate Stark (God Mode)")
st.write(
    "System Status: Online | Live Lite Search & Task Management Active"
    " (100% Free, No Google)"
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

# استقبال مدخلات المستخدم بالعامية المصرية أو الإنجليزية
if query := st.chat_input("كلمني بالعامية المصرية أو الإنجليزية يا سيدي..."):
  st.chat_message("user").markdown(query)
  st.session_state.messages.append({"role": "user", "content": query})

  query_lower = query.lower()
  response = ""

  is_english = any(
      ord(char) < 128 and char.isalpha() for char in query
  ) and not any(
      ar_word in query
      for ar_word in [
          "فين",
          "إيه",
          "كام",
          "الساعة",
          "ازيك",
          "عايز",
          "ايه",
          "الجو",
          "ليه",
          "مين",
      ]
  )

  # 1. الوقت والتاريخ
  if (
      "time" in query_lower
      or "الساعة" in query_lower
      or "الوقت" in query_lower
  ):
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    if is_english:
      response = f"The time is {str_time}, Sir. Time flies when you're building the future."
    else:
      response = f"الساعة دلوقتي يا سيدي {str_time}، الوقت بيعدي وإحنا بنبتكر."

  # 2. إدارة المهام وتنظيم الحياة
  elif (
      "مهمة" in query_lower
      or "task" in query_lower
      or "اضف" in query_lower
      or "add" in query_lower
  ):
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

  # 3. البحث المباشر السريع باستخدام DuckDuckGo Lite (بدون جوجل وبدون أخطاء)
  else:
    try:
      url = "https://lite.duckduckgo.com/lite/"
      data = {"q": query}
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          )
      }
      res = requests.post(url, data=data, headers=headers, timeout=5)

      if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        snippets = []
        results = soup.find_all("td", class_="result-snippet")
        for r in results[:3]:
          text = r.get_text(strip=True)
          if text:
            snippets.append(f"• {text}")

        if snippets:
          joined_snippets = "\n\n".join(snippets)
          response = (
              f"**[Stark Live Search Protocol]:**\n\n{joined_snippets}\n\n*النتائج قدامك يا سيدي من قلب الويب مباشرة وبدون لف ودوران.*"
              if not is_english
              else f"**[Stark Live Search Protocol]:**\n\n{joined_snippets}\n\n*Here are the live web results, Sir.*"
          )
        else:
          response = (
              f"دورت على '{query}' بس ملقيتش تفاصيل واضحة يا سيدي."
              if not is_english
              else f"Searched for '{query}', but found no clear details, Sir."
          )
      else:
        response = (
            "السيرفر بياخد بريك قصير يا سيدي، جرب سؤالاً آخر."
            if not is_english
            else "The server is taking a short break, Sir. Try another query."
        )
    except Exception as e:
      response = (
          f"حصل خطأ بسيط أثناء البحث يا سيدي: {str(e)}"
          if not is_english
          else f"An error occurred while searching, Sir: {str(e)}"
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
