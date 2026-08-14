import streamlit as st
import google.generativeai as genai

# إعداد مفتاح جوجل جيميني
genai.configure(api_key="AQ.Ab8RN6JQ97NtHF9qPklEauCrAESCvrpOPlHYo7sRU1hpgWj4Jw")

st.title("🤖 Jarvis")

# اختيار موديل جيميني السريع
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("...اكتب رسالتك هنا"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # تجهيز السجل وتجهيز الرد
    chat_history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
        for m in st.session_state.messages[:-1]
    ]
    
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(prompt)
    assistant_response = response.text

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
