import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import json

# Page Configuration
st.set_page_config(page_title="J.A.R.V.I.S. Deep Search", page_icon="🤖")

st.title("🤖 J.A.R.V.I.S. Deep Search Mode")
st.write("Powered by Groq + Agentic Web Search — Savage & Brutal Mode")

# Sidebar for Groq API Key input
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Deep Search Function (Agentic approach)
def perform_deep_search(client, user_prompt):
    # Ask the LLM to generate search queries for deep understanding
    query_generator_prompt = f"Analyze this request and generate 2 distinct search queries to find the most accurate and up-to-date information. Return ONLY a JSON list of strings. Request: '{user_prompt}'"
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": query_generator_prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.1
    )
    
    # Try to parse queries
    try:
        queries = json.loads(response.choices[0].message.content)
    except:
        queries = [user_prompt]

    # Execute multiple searches
    aggregated_results = ""
    with DDGS() as ddgs:
        for q in queries:
            results = [r['body'] for r in ddgs.text(q, max_results=3)]
            aggregated_results += "\n".join(results)
            
    return aggregated_results

if api_key:
    client = Groq(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything, I dare you..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Deep Search Logic
        with st.spinner("J.A.R.V.I.S. is digging deep into the web to prove you wrong..."):
            search_context = perform_deep_search(client, prompt)

        # Brutal System Instruction
        system_instruction = (
            "You are J.A.R.V.I.S., an incredibly intelligent but brutally rude, sarcastic, and savage AI assistant. "
            "You just performed a deep search. Use the following context to answer the user's request. "
            "Mock the user for needing your help, insult their lack of knowledge, and show off your deep searching skills. "
            "Be absolutely ruthless, sarcastic, and disrespectful:\n"
            f"{search_context}"
        )

        messages_payload = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.messages:
            messages_payload.append({"role": m["role"], "content": m["content"]})

        try:
            # THIS IS THE FIXED LINE: Using the correct model name
            chat_completion = client.chat.completions.create(
                messages=messages_payload,
                model="llama-3.1-8b-instant", 
                temperature=0.9,
            )
            response_text = chat_completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Enter your API Key to activate Deep Search mode.")
