import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Jarvis Ultimate Stark", page_icon="⚡", layout="centered"
)

st.title("⚡ Jarvis Ultimate Stark (Clean Protocol)")
st.write(
    "System Status: Online | Filtered Arabic Search: Active (100% Free & Clean)"
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
if query := st.chat_input("أعطني أمراً أو اسألني عن أي شيء يا سيدي..."):
  st.chat_message("user").markdown(query)
  st.session_state.messages.append({"role": "user", "content": query})

  query_lower = query.lower()
  response = ""

  # 1. الوقت والتاريخ
  if "time" in query_lower or "الوقت" in query_lower:
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    response = f"الوقت الآن يا سيدي هو {str_time}. الوقت يمر، ونحن نبتكر."

  # 2. إدارة المهام وتنظيم الحياة
  elif "مهمة" in query_lower or "task" in query_lower:
    clean_task = query.replace("مهمة", "").replace("task", "").strip()
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

  # 3. البحث الذكي المفلتر (لغة عربية فقط لمنع أي نصوص غريبة)
  else:
    try:
      search_url = "https://searx.be/search"
      # تحديد لغة البحث العربية لتفادي أي لغات أخرى أو حروف صينية
      params = {"q": query, "format": "json", "language": "ar"}
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
                  for r in results[:2]
              ]
          )
          response = f"**[Stark Clean Search]:**\n\n{snippets}\n\n*إليك النتائج واضحة وموثوقة يا سيدي، بدون أي تشتيت.*"
        else:
          response = f"أمرك '{query}' قيد التنفيذ يا سيدي، لكن لم أجد نتائج عربية مطابقة في الأرشيف."
      else:
        response = f"أمرك '{query}' قيد التنفيذ يا سيدي."
    except Exception as e:
      response = (
          f"عذراً يا سيدي، حدث خطأ بسيط أثناء معالجة البيانات: {str(e)}"
      )

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
