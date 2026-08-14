import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="Jarvis", page_icon="🤖")
st.title("🤖 Jarvis")

client = OpenAI(api_key=os.environ.get("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"))

with st.sidebar:
    st.write("💬 GPT-3.5 Turbo")
    if st.button("🗑️ مسح"):
        st.session_state.msgs = []
        st.rerun()

if "msgs" not in st.session_state:
    st.session_state.msgs = [{"role": "assistant", "content": "أهلاً بك! 👋"}]

for msg in st.session_state.msgs:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.msgs.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    res = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.msgs)
    reply = res.choices[0].message.content
    
    st.chat_message("assistant").write(reply)
    st.session_state.msgs.append({"role": "assistant", "content": reply})
