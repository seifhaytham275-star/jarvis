import streamlit as st
import requests

# إعداد الصفحة
st.set_page_config(page_title="Jarvis | Groq & Perplexity", page_icon="🤖")

# تهيئة الجلسة لكل مستخدم
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Good day, Sir. Jarvis systems are online."}]

# الـ Settings الجانبية
st.sidebar.title("⚙️ Jarvis Settings")
provider = st.sidebar.selectbox("Choose AI Provider", ["Groq", "Perplexity"])
api_key = st.sidebar.text_input("API Key:", type="password")

if provider == "Groq":
    model = st.sidebar.selectbox("Select Model", ["llama3-8b-8192", "llama3-70b-8192"])
else:
    model = st.sidebar.selectbox("Select Model", ["sonar", "sonar-reasoning"])

st.sidebar.markdown("---")
st.sidebar.info("Developed by the genius Seif.")

st.title(f"🌐 Jarvis | {provider}")

# عرض الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# منطق الرد
if prompt := st.chat_input("Ask Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # التحقق من بصمة المطور
        if any(word in prompt.lower() for word in ["مين عملك", "who created you"]):
            response = "تم تصميمي وتطويري بواسطة العبقري سيف."
        else:
            if not api_key:
                response = "Please enter your API Key in Jarvis Settings."
            else:
                if provider == "Groq":
                    url = "https://api.groq.com/openai/v1/chat/completions"
                else:
                    url = "https://api.perplexity.ai/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are Jarvis, created by the genius Seif. Respond in the user's language accurately."},
                        {"role": "user", "content": prompt}
                    ]
                }
                
                try:
                    res = requests.post(url, headers=headers, json=payload)
                    
                    if res.status_code == 200:
                        response = res.json()['choices'][0]['message']['content']
                    else:
                        response = f"API Error ({res.status_code}): {res.text}"
                        
                except Exception as e:
                    response = f"Connection error: {str(e)}"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
