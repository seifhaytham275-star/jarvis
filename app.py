import streamlit as st
from groq import Groq
from googlesearch import search

# Page Configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Jarvis AI Assistant")
st.write("System Status: Online & Operational (Clean Multi-Language + Web Search)")

# Sidebar for API Key configuration
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to search Google
def search_web(query):
    try:
        urls = []
        for url in search(query, num_results=3):
            urls.append(url)
        return "\n".join(urls)
    except Exception as e:
        return f"Search error: {e}"

# Handle user input
if prompt := st.chat_input("Type your message to Jarvis..."):
    if not groq_api_key:
        st.warning("Please enter your Groq API Key in the sidebar settings.")
    else:
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check if the user is asking to search the web
        enhanced_prompt = prompt
        if "search" in prompt.lower() or "بحث" in prompt or "اكتب عن" in prompt:
            with st.status("Searching the web...", expanded=False):
                search_results = search_web(prompt)
                enhanced_prompt = f"User query: {prompt}\n\nHere are some web search links/results to help you:\n{search_results}"

        try:
            # Initialize Groq client
            client = Groq(api_key=groq_api_key)
            
            chat_history = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages[:-1]
            ]
            chat_history.append({"role": "user", "content": enhanced_prompt})
            
            # System prompt updated to strictly prevent mixing random languages/Chinese characters
            system_message = {
                "role": "system",
                "content": (
                    "You are Jarvis, an advanced AI assistant. You are fully fluent in all languages of the world. "
                    "Always detect the user's language and respond strictly and cleanly in that exact same language. "
                    "CRITICAL: Never mix random languages, Chinese characters, or unrelated scripts into your response unless explicitly requested. "
                    "Keep your responses clear, natural, and completely understandable."
                )
            }
            
            messages_payload = [system_message] + chat_history

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
            )
            
            response_text = completion.choices[0].message.content

            # Append assistant response to history and display
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
                
        except Exception as e:
            st.error(f"Error connecting to Groq: {e}")
