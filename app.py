import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Jarvis AI Assistant")
st.write("System Status: Online & Operational")

# Sidebar for API Key configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Type your message to Jarvis..."):
    if not api_key:
        st.warning("Please enter your Groq API Key in the sidebar settings.")
    else:
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Initialize Groq client
            client = Groq(api_key=api_key)
            
            chat_history = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_history,
            )
            
            response_text = completion.choices[0].message.content

            # Append assistant response to history and display
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
                
        except Exception as e:
            st.error(f"Error connecting to Groq: {e}")
