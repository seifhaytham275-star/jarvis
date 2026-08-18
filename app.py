import streamlit as st

# 1. قاعدة المعرفة الكاملة والبروفايل الشخصي لجارفيس
user_profile = {
    "name": "سيف هيثم سعيد عبد الخالق حسانين خليفة المصري",
    "age": "15 سنة (مواليد 27 مايو 2011)",
    "education": "طالب في نظام الثانوية المصرية الجديد (المنهج الجديد / العلوم المتكاملة)",
    "football": "لاعب كرة قدم ناشئ ومنضم رسمياً لأكاديمية أرسنال للناشئين",
    "gaming": {
        "rocket_league": "تصنيف Super Sonic Legend (SSL)، محترف في الـ Air Dribbles والـ Pinch Saves",
        "fortnite": "تصنيف Unreal، يلعب Build mode، بيفضل سكينز (Tony Stark, Haven, Tart Tycoon) وبايتكس (Ice Breaker)",
        "consoles": "يلعب على PlayStation 4 و PlayStation 5"
    },
    "interests_and_hobbies": [
        "مصارعة WWE ومتابعة العروض الكبرى مثل SummerSlam و Survivor Series",
        "عالم مارفل السينمائي وسبايدرمان وتفاصيل أفلام مثل Spider-Man: Brand New Day",
        "صناعة وتصميم Web-Shooters ميكانيكية منزلية باستخدام أقلام، أستك، خيوط كروشيه، وستان",
        "تطوير الذكاء الاصطناعي ومساعدين بأسماء EDITH أو Jarvis باستخدام Java (مشروع مدرسة استمر 9 شهور)، Voiceflow، Character.ai، و Hugging Face",
        "بناء هاردوير وبروتوتيبات ب microcontroller وكاميرات وهيدست wearable"
    ],
    "fitness": {
        "routine": "Push-Pull-Legs (PPL) جيم سبلت صارم",
        "cardio_calisthenics": "تمارين كالتستكس عالية الش intensidad مثل CrossFit Cindy workout"
    },
    "music": [
        "Billie Eilish", "Michael Jackson", "Eminem", 
        "Central Cee", "Sabrina Carpenter", "Justin Bieber", "Madison Beer"
    ],
    "family": "عنده أخترين أكبر منه، وأخت صغيرة، وعمته الحبيبة (Aunt May)",
    "lifestyle": "شعر كيرلي (بيستعمل leave- بيئة كريم)، وبيموت في شاورما الفراخ البيتية مع الرز، الكبدة، المكرونة، والبطاطس والمياه الغازية"
}

st.set_page_config(page_title="Jarvis AI - Ultimate Core", page_icon="🤖")
st.title("🤖 Jarvis - Ultimate Neural Core")
st.write(f"مرحباً بك يا سيدي، **سيف**. قاعدة البيانات والأنظمة السيبرانية بالكامل متصلة وجاهزة.")

# 2. إدارة حالة الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. عرض رسائل الشات القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. محرك الردود الذكي المعتمد على بيانات سيف الحقيقية
def get_jarvis_response(prompt):
    p = prompt.lower()
    
    if any(k in p for k in ["من أنا", "اسمى", "اسمي", "مين أنا"]):
        return f"أنت **{user_profile['name']}**، بطلنا صاحب الـ 15 سنة، لاعب ناشئين أرسنال، والمبرمج العبقري وراء تطويري!"
    
    elif any(k in p for k in ["تمرين", "جيم", "ppl", "عضلات", "تخسيس"]):
        return f"الجدول بتاعك يا سيف ماشي على نظام الـ **{user_profile['fitness']['routine']}** القوي، ومع تمرينات الكالتستكس زي الـ Cindy workout، مستواك البدني في حتة تانية. شد حيلك وخلص تمريرتك اليومية!"
    
    elif any(k in p for k in ["أرسنال", "كورة", "كرة قدم", "ماتش"]):
        return f"بصفتك لاعب رسمي في ناشئين أرسنال ({user_profile['football']})، التركيز واللعب الجماعي هما مفتاحك للاحتراف العالمي. جاهز للتدريب الجاي؟"
    
    elif any(k in p for k in ["لعبة", "بي سي", "بلايستيشن", "روم", "روكيت", "فورتنايت"]):
        return f"أنت مبدع في الجيمنج يا سيف! في Rocket League محقق **{user_profile['gaming']['rocket_league']}**، وفي Fortnite واصل **Unreal** بالـ Build mode وسكين Tony Stark. وحش بمعنى الكلمة!"
    
    elif any(k in p for k in ["web-shooter", "سقالة", "عنكبوت", "مارفل", "سبايدرمان"]):
        return f"مشروع الـ Web-Shooters الميكانيكية بتاعتك (بالأقلام والأستك والخيوط) مع تفاصيل عالم مارفل و Spider-Man: Brand New Day بيثبت إنك مخترع حقيقي مش مجرد مبرمج!"
    
    elif any(k in p for k in ["برمجة", "كود", "جافا", "java", "ذكاء اصطناعي", "ai", "مشروع"]):
        return f"دماغك البرمجية اللي طورت مشروع المدرس بـ Java لمدة 9 شهور، وشغال على Voiceflow و Hugging Face، هي اللي مخلياني أقدر أرد عليك بالدقة دي. مستعد نكتب كود جديد؟"
    
    elif any(k in p for k in ["موسيقى", "اغاني", "أغنية", "مطرب"]):
        return f"أكيد المزيكا بتظبط دماغك وأنت شغال على الكود! خصوصاً لما تسمع لـ Billie Eilish أو Eminem أو Central Cee."
    
    else:
        return f"أنا مسجل كل تفاصيلك يا سيف (من البرمجة لحد أرسنال والجيم والألعاب). قولي إيه الفكرة الجديدة اللي عايز ننفذها سوا في الكود النهاردة؟"

# 5. استقبال المدخلات وتشغيل الشات
if prompt := st.chat_input("اطرح أمرك على جارفيس..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_jarvis_response(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
