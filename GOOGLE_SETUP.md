# توصيل JARVIS بـ Gmail و Google Drive

## الفكرة
عشان JARVIS يقدر يدخل على إيميلك وملفاتك، محتاج **إذنك الصريح** عبر OAuth —
مفيش طريقة تانية آمنة تخلي أي برنامج يوصل لحسابك الشخصي على جوجل. الخطوات
دي مرة واحدة بس.

---

## الخطوات

### 1) اعمل مشروع على Google Cloud Console
1. روح على https://console.cloud.google.com
2. اعمل **New Project** (أي اسم، زي "jarvis-assistant")

### 2) فعّل الـ APIs المطلوبة
من نفس المشروع، روح **APIs & Services → Library** وفعّل الاتنين دول:
- **Gmail API**
- **Google Drive API**

### 3) اظبط شاشة الموافقة (OAuth consent screen)
- **APIs & Services → OAuth consent screen**
- اختار **External** (لو حساب Gmail عادي) أو **Internal** (لو Google Workspace)
- املا الاسم والإيميل بتاعك بس (مفيش حاجة تانية مطلوبة لاستخدام شخصي)
- في **Test users**، ضيف إيميل الجيميل بتاعك نفسه

### 4) اعمل OAuth Client ID
- **APIs & Services → Credentials → Create Credentials → OAuth client ID**
- نوع التطبيق: **Desktop app**
- بعد الإنشاء، دوس **Download JSON**
- سمّي الملف **`credentials.json`** وحطه في نفس فولدر المشروع (جنب `app.py`)

### 5) ثبّت المكتبات المطلوبة
```bash
pip install -r requirements.txt
```

### 6) شغّل التطبيق واربط حسابك
```bash
streamlit run app.py
```
من الـ sidebar، تحت "GOOGLE ACCESS"، دوس **🔗 CONNECT GOOGLE**.
هيفتحلك تاب متصفح تسجّل دخول وتوافق على الصلاحيات. بعد الموافقة، هيتحفظ
ملف `token.json` تلقائيًا في نفس الفولدر — ومش هتحتاج تكرر الخطوة دي تاني.

---

## ملاحظات مهمة
- الصلاحيات المطلوبة **قراءة فقط** (readonly) — JARVIS يقدر يقرا إيميلاتك
  وملفاتك، مش يبعت أو يمسح أو يعدّل حاجة.
- **متشاركش `credentials.json` ولا `token.json` مع حد ولا في صور/سكرين شوتس**
  — أي حد يوصلهم يقدر يقرا إيميلاتك وملفاتك.
- لو غيّرت جهاز أو مسحت `token.json`، هتحتاج تعمل CONNECT GOOGLE تاني بس.
- التطبيق لسه في وضع "Testing" في Google Cloud — يعني بيشتغل بس مع الإيميلات
  اللي ضفتها في Test users (خطوة 3). ده كافي تمامًا لاستخدامك الشخصي.
