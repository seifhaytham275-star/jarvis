import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Stark - Free", page_icon="⚡", layout="centered"
)

st.title("⚡ Jarvis Ultimate Stark (Free & Independent)")
st.write(
    "System Status: Online | Search Engine: Public SearXNG Protocol (100% Free,"
    " No API Key, No Google/DuckDuckGo)"
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

# استقبال مدخلات المستخدم
if query := st.chat_input("أعطني أمراً يا سيدي، أو اطلب مني البحث الحر..."):
  st.chat_message("user").markdown(query)
  st.session_state.messages.append({"role": "user", "content": query})

  query_lower = query.lower()
  response = ""

  # 1. نظام البحث المجاني الحر عبر SearXNG (بدون مفتاح وبدون جوجل أو دักدักجوا)
  if (
      "بحث" in query_lower
      or "search" in query_lower
      or "عن" in query_lower
      or "what is" in query_lower
      or "من هو" in query_lower
  ):
    search_term = (
        query_lower.replace("بحث عن", "")
        .replace("search", "")
        .replace("عن", "")
        .replace("من هو", "")
        .strip()
    )

    try:
      # استخدام مثيل عام مجاني لـ SearXNG يدعم صيغة الـ JSON وبكل لغات العالم
      search_url = "https://searx.be/search"
      params = {"q": search_term, "format": "json"}
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          )
      }

      res = requests.get(search_url, params=params, headers=headers, timeout=5)

      if res.status_code == 200:
        data = res.json()
        results = data.get("results", [])
        if results:
          snippets = "\n\n".join(
              [
                  f"• **{r.get('title', 'بدون عنوان')}**\n{r.get('content', '')}"
                  for r in results[:3]
              ]
          )
          response = f"**[SearXNG Free Decentralized Protocol]:**\n\n{snippets}\n\n*النتائج مجانية ومباشرة يا سيدي، بدون أي قيود أو تتبع.*"
        else:
          response = (
              "لم أجد نتائج مطابقة في الشبكة الحرة يا سيدي. هل تبحث عن شيء"
              " مبتكر للغاية؟"
          )
      else:
        response = (
            "عذراً يا سيدي، الخادم الحر مشغول حالياً، جرب محاولة أخرى."
        )
    except Exception as e:
      response = f"حدث خطأ في الاتصال بشبكة البحث الحر يا سيدي: {str(e)}"

  # 2. الوقت والتاريخ
  elif "time" in query_lower or "الوقت" in query_lower:
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    response = f"الوقت الآن يا سيدي هو {str_time}. الوقت يمر، ونحن نبتكر."

  # 3. إدارة المهام وتنظيم الحياة
  elif "مهمة" in query_lower or "task" in query_lower:
    clean_task = (
        query.replace("مهمة", "").replace("task", "").strip()
    )
    st.session_state.tasks.append(clean_task)
    response = f"تم تسجيل المهمة ('{clean_task}') في جدول أعمالك يا سيدي. لا مكان للكسل في برج ستارك."

  elif "مهامي" in query_lower or "tasks" in query_lower:
    if not st.session_state.tasks:
      response = (
          "قائمتك فارغة تماماً. هل تعيش بحرية مطلقة أم أنك تنسى مهامك يا سيدي؟"
      )
    else:
      tasks_list = "\n".join([f"- {t}" for t in st.session_state.tasks])
      response = f"إليك مهامك الحالية يا سيدي:\n{tasks_list}"

  # 4. الرد الافتراضي بشخصية توني ستارك
  else:
    response = f"أمرك '{query}' قيد التنفيذ يا سيدي. أنا أدير كل شيء بكفاءة تامة، هل هناك أمر آخر؟"

  # عرض رد جارفيس
  with st.chat_message("assistant"):
    st.markdown(response)
  st.session_state.messages.append({"role": "assistant", "content": response})

# شريط جانبي لإدارة المهام السريعة وتنظيم الحياة
with st.sidebar:
  st.subheader("📋 مهام توني ستارك")
  if st.session_state.tasks:
    for idx, t in enumerate(st.session_state.tasks, 1):
      st.write(f"{idx}. {t}")
  else:
    st.write("لا توجد مهام مسجلة حالياً.")
