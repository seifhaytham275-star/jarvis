import streamlit as st
from streamlit_mic_recorder import speech_to_text
from groq import Groq

client = Groq(api_key="حط_مفتاح_الـ_Groq_هنا")
st.title("🐱‍👤 Jarvis")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

audio_text = speech_to_text(language='ar', start_prompt="🎙️ اضغط للتحدث", stop_prompt="جاري الاستماع...", just_once=True)
prompt = st.chat_input("اكتب رسالتك هنا...") or audio_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
