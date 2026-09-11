# توصيل JARVIS بواتساب — دليل الإعداد

## الفكرة
`whatsapp_bot.py` سيرفر Flask منفصل تمامًا عن تطبيق Streamlit. بيستقبل رسايل
واتساب حقيقية عبر **WhatsApp Cloud API** الرسمي من Meta (مجاني في الاستخدام، بس
لازم يكون عندك رابط HTTPS عام عشان Meta تقدر توصله).

---

## الخطوات

### 1) اعمل Meta Developer App
1. روح على https://developers.facebook.com وسجل كـ Developer (لو معملتش قبل كده).
2. اعمل **Create App** → اختار نوع **Business**.
3. من صفحة المنتجات، دوس **Set up** جنب **WhatsApp**.
4. Meta هتديك تلقائيًا:
   - رقم تجريبي مجاني (Test Number)
   - **Phone Number ID**
   - **Access Token** مؤقت (24 ساعة) — كويس للتجربة بس

### 2) لو عايز التوكن يكون دائم (مش بيتجدد كل يوم)
من **Business Manager → Users → System Users** اعمل System User، اديله صلاحيات
`whatsapp_business_messaging` و `whatsapp_business_management`، وطلع منه توكن دائم.

### 3) جهّز الإعدادات
هتحتاج 4 قيم، حطهم كـ environment variables أو مباشرة في أول `whatsapp_bot.py`:

```
WHATSAPP_TOKEN   = التوكن من الخطوة 1 أو 2
PHONE_NUMBER_ID  = من نفس صفحة API Setup
VERIFY_TOKEN     = أي نص سري تخترعه إنت بنفسك (مثلاً: jarvis_secret_2026)
GEMINI_API_KEY   = مفتاح Gemini بتاعك
```

### 4) شغّل السيرفر محليًا
```bash
pip install -r requirements_whatsapp.txt
python whatsapp_bot.py
```
هيشتغل على `http://localhost:8080`.

### 5) اعمل السيرفر متاح للعالم الخارجي (Meta محتاجة HTTPS عام)
أسهل حل للتجربة: **ngrok**
```bash
ngrok http 8080
```
هيديك رابط زي `https://xxxx.ngrok-free.app` — انسخه.

### 6) ظبط الـ Webhook في Meta
من صفحة الـ App بتاعتك: **WhatsApp → Configuration → Webhooks**
- **Callback URL**: `https://xxxx.ngrok-free.app/webhook`
- **Verify Token**: نفس القيمة اللي حطيتها في `VERIFY_TOKEN`
- دوس **Verify and Save**
- اشترك (Subscribe) في حقل `messages`

### 7) ضيف رقمك كـ Tester
لسه الرقم التجريبي مش هيقدر يبعت لأي رقم — لازم تضيف رقم موبايلك الشخصي كـ
**Recipient number** من نفس صفحة API Setup (فيه زرار "Manage phone number list").

### 8) جرّب
ابعت رسالة واتساب من موبايلك للرقم التجريبي، وJARVIS هيرد عليك بـ Gemini فورًا.

---

## ملاحظات مهمة
- **التوكن المؤقت بينتهي كل 24 ساعة** — لو السيرفر وقف يرد، رجّع اطلع توكن جديد
  أو اعمل System User token دائم زي الخطوة 2.
- **رابط ngrok بيتغير كل مرة تشغّله** إلا لو عندك حساب مدفوع أو domain ثابت —
  هتحتاج تحدّث الـ Callback URL في Meta كل مرة تعيد تشغيل ngrok.
- للاستخدام الدائم (مش مجرد تجربة)، الأفضل تنشر `whatsapp_bot.py` على استضافة
  فيها رابط HTTPS ثابت (Render / Railway / Fly.io عندهم free tier).
- **متنشرش أي توكن أو API key في صور أو سكرين شوتس** زي ما حصل قبل كده.
