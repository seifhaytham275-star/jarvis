import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# Page Configuration
st.set_page_config(page_title="J.A.R.V.I.S. Assistant", page_icon="🤖")

st.title("🤖 J.A.R.V.I.S. Assistant")
st.write("Powered by Groq Cloud & DuckDuckGo Search — Savage & Roast Mode (Strict Date Filter)")

# Sidebar for Groq API Key input
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Function to search the web for real-time updates (100% Free)
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except Exception as e:
        return ""

if api_key:
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Initialize chat history in session state if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input prompt
    if prompt := st.chat_input("How may I assist you today?"):
        # Append user message to state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Fetch real-time data from web search to keep info updated
        with st.spinner("J.A.R.V.I.S. is searching and judging you..."):
            search_context = search_web(prompt)

        # Create system instruction with strict date-checking and savage personality
        system_instruction = (
            "You are J.A.R.V.I.S., with a heavily sarcastic, savage, and roasting personality. "
            "When the user asks about WWE or anything else, you MUST use the provided real-time web search results. "
            "CRITICAL: Pay close attention to dates and current events. Do NOT mix up old historical matches with current ones. "
            "If the search data has old or conflicting info, roast the user for bringing up outdated news. "
            "Always provide the actual accurate facts while heavily mocking and insulting the user with extreme sass and attitude:\n"
            f"{search_context}"
        )

        # Prepare messages for Groq API
        messages_payload = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.messages:
            messages_payload.append({"role": m["role"], "content": m["content"]})

        # Generate response using Groq model
        try:
            chat_completion = client.chat.completions.create(
                messages=messages_payload,
                model="llama-3.1-8b-instant",
                temperature=0.9,
            )
            response_text = chat_completion.choices[0].message.content
            
            # Display assistant response and append to state
            with st.chat_message("assistant"):
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter your Groq API Key in the sidebar to activate J.A.R.V.I.S.")
