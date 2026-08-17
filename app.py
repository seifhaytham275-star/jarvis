import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Stark", page_icon="⚡", layout="centered"
)

st.title("⚡ Jarvis Ultimate Stark (Wikidata Protocol)")
st.write(
    "System Status: Online | Knowledge Graph Active (100% Free, No API Key, No"
    " Timeouts)"
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
      response = f"الساعة دلوقتي يا سيدي {str_time}, الوقت بيعدي وإحنا بنبتكر."

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

  # 3. البحث الذكي المستقر عبر Wikidata API
  else:
    try:
      url = "https://www.wikidata.org/w/api.php"
      params = {
          "action": "wbsearchentities",
          "search": query,
          "language": "en" if is_english else "ar",
          "format": "json",
      }
      headers = {"User-Agent": "JarvisStarkBot/1.0 (StarkTower)"}

      res = requests.get(url, params=params, headers=headers, timeout=5)

      if res.status_code == 200:
        data = res.json()
        search_results = data.get("search", [])
        if search_results:
          snippets = "\n\n".join(
              [
                  f"• **{r.get('label', '')}**\n{r.get('description', 'لا توجد تفاصيل إضافية')}"
                  for r in search_results[:3]
              ]
          )
          response = (
              f"**[Stark Wikidata Intelligence]:**\n\n{snippets}\n\n*البيانات مستخرجة بدقة تامة يا سيدي وبدون أي تقطيع.*"
              if not is_english
              else f"**[Stark Wikidata Intelligence]:**\n\n{snippets}\n\n*Here are the precise details, Sir.*"
          )
        else:
          response = (
              f"دورت على '{query}' في قاعدة البيانات بس ملقيتش نتائج مطابقة يا سيدي."
              if not is_english
              else f"Searched for '{query}' in the database, but found no matching results, Sir."
          )
      else:
        response = (
            "حصل خطأ بسيط في الاتصال بقاعدة البيانات يا سيدي، جرب سؤالاً آخر."
            if not is_english
            else "A slight connection error occurred, Sir. Try another query."
        )
    except Exception as e:
      response = (
          f"حدث خطأ تقني يا سيدي: {str(e)}"
          if not is_english
          else f"Technical error occurred, Sir: {str(e)}"
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
