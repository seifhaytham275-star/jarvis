import streamlit as st
import requests
import json
from datetime import datetime

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="J.A.R.V.I.S. Prime",
    page_icon="🤖",
    layout="wide"
)

# ===================== SESSION STATE =====================
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ""
if 'serper_api_key' not in st.session_state:
    st.session_state.serper_api_key = ""
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False
if 'mic_enabled' not in st.session_state:
    st.session_state.mic_enabled = False
if 'arabic_mix' not in st.session_state:
    st.session_state.arabic_mix = False
if 'model_name' not in st.session_state:
    st.session_state.model_name = "llama-3.3-70b-versatile"
if 'key_tested' not in st.session_state:
    st.session_state.key_tested = False

# ===================== SIDEBAR - API KEYS & SETTINGS =====================
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # ===== API KEYS SECTION =====
    st.subheader("🔑 API Keys")
    
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        value=st.session_state.groq_api_key,
        help="Get your free key from console.groq.com - no credit card required!"
    )
    if groq_key:
        st.session_state.groq_api_key = groq_key
    
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        placeholder="Enter Serper API key...",
        value=st.session_state.serper_api_key,
        help="Get your key from serper.dev (optional)"
    )
    if serper_key:
        st.session_state.serper_api_key = serper_key
    
    # API Key Status
    if st.session_state.groq_api_key:
        st.success("✅ Groq API Key set")
    else:
        st.warning("⚠️ Groq API Key required")
    
    st.divider()
    
    # ===== MODEL SELECTION =====
    st.subheader("🧠 Model Selection")
    
    model_options = [
        "llama-3.3-70b-versatile",    # ✅ Best free model - 128K context
        "llama-3.1-8b-instant",        # ✅ Fastest model
        "llama-3.2-90b-vision-preview", # ✅ Vision model
        "llama-3.2-11b-vision-preview", # ✅ Smaller vision model
        "mixtral-8x7b-32768",          # ✅ Good for reasoning
        "gemma2-9b-it",                # ✅ Google's model
        "gpt-oss-120b",                # ✅ 120B parameter model
        "gpt-oss-20b",                 # ✅ 20B parameter model
        "qwen-3.2-32b",                # ✅ Qwen model
    ]
    
    selected_model = st.selectbox(
        "Select Model",
        options=model_options,
        index=0,
        help="Choose a model that works with your API key"
    )
    
    if selected_model:
        st.session_state.model_name = selected_model
        st.info(f"🧠 Using: {selected_model}")
    
    st.divider()
    
    # ===== FEATURES =====
    st.subheader("🎛️ Features")
    
    st.session_state.voice_enabled = st.toggle(
        "🔊 Voice Response",
        value=st.session_state.voice_enabled
    )
    
    st.session_state.mic_enabled = st.toggle(
        "🎤 Microphone",
        value=st.session_state.mic_enabled
    )
    
    st.session_state.arabic_mix = st.toggle(
        "🌍 Mix Eloquent/Slang Arabic",
        value=st.session_state.arabic_mix
    )
    
    st.divider()
    
    # ===== CHAT HISTORY =====
    st.subheader("📜 Chat History")
    if st.session_state.messages:
        for i, msg in enumerate(st.session_state.messages[-5:]):
            if msg["role"] == "user":
                st.caption(f"👤 {msg['content'][:25]}...")
            else:
                st.caption(f"🤖 {msg['content'][:25]}...")
    else:
        st.caption("No messages yet")
    
    st.divider()
    
    # ===== ACTIONS =====
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.key_tested = False
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.messages = []
            st.session_state.groq_api_key = ""
            st.session_state.serper_api_key = ""
            st.session_state.key_tested = False
            st.rerun()
    
    st.divider()
    
    # ===== STATUS =====
    st.caption(f"🟢 Status: {'Ready' if st.session_state.groq_api_key else 'No API Key'}")
    st.caption(f"📡 Model: {st.session_state.model_name}")
    st.caption(f"💬 Messages: {len(st.session_state.messages)}")

# ===================== MAIN CHAT INTERFACE =====================
st.title("🤖 J.A.R.V.I.S. Prime")
st.caption("At your command, Sir...")

# ===================== HELPER FUNCTIONS =====================
def search_web(query):
    """Search using Serper API"""
    if not st.session_state.serper_api_key:
        return None
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": st.session_state.serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            results = response.json()
            snippets = []
            for item in results.get("organic", [])[:3]:
                snippets.append(f"- {item.get('title', '')}: {item.get('snippet', '')}")
            return "\n".join(snippets) if snippets else None
    except:
        pass
    return None

def get_groq_response(prompt, web_results=None):
    """Get response from Groq API"""
    if not st.session_state.groq_api_key:
        return "⚠️ Please enter your Groq API Key in the sidebar."
    
    # Prepare the prompt with web results if available
    full_prompt = prompt
    if web_results:
        full_prompt = f"{prompt}\n\n🔍 Web Search Results:\n{web_results}"
    
    # Groq API endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {st.session_state.groq_api_key}",
        "Content-Type": "application/json"
    }
    
    # Build system message
    system_msg = "You are J.A.R.V.I.S., Tony Stark's AI assistant. Be helpful, witty, and professional."
    
    if st.session_state.arabic_mix:
        system_msg += " Mix eloquent Arabic with English and some slang Arabic when appropriate."
    
    # Prepare messages
    messages = [
        {"role": "system", "content": system_msg}
    ]
    
    # Add last 10 messages for context
    for msg in st.session_state.messages[-10:]:
        messages.append(msg)
    
    # Add current prompt
    messages.append({"role": "user", "content": full_prompt})
    
    # ===== USING SELECTED MODEL =====
    payload = {
        "model": st.session_state.model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            error = response.json()
            error_msg = error.get("error", {}).get("message", str(response.text))
            error_type = error.get("error", {}).get("type", "")
            
            # ===== HANDLE RATE LIMIT ERROR =====
            if "rate" in error_type.lower() or "rate" in str(response.status_code):
                return (
                    "⏰ **Rate Limit Reached**\n\n"
                    "Groq free tier limits:\n"
                    "• **30 requests per minute**\n"
                    "• **20,000 tokens per minute**\n"
                    "• **14,400 requests per day**\n\n"
                    "**What to do:**\n"
                    "1️⃣ Wait 1-2 minutes and try again\n"
                    "2️⃣ The daily limit resets at midnight (UTC)\n"
                    "3️⃣ Consider using a different model from the dropdown\n\n"
                    f"Error: {error_msg}"
                )
            
            # ===== HANDLE MODEL NOT FOUND ERROR =====
            elif "model_not_found" in error_type or "404" in str(response.status_code):
                return (
                    f"❌ **Model '{st.session_state.model_name}' not found.**\n\n"
                    f"**Available models on Groq:**\n"
                    "• `llama-3.3-70b-versatile` (Best, 128K context)\n"
                    "• `llama-3.1-8b-instant` (Fastest)\n"
                    "• `mixtral-8x7b-32768` (Good for reasoning)\n"
                    "• `gemma2-9b-it` (Google's model)\n"
                    "• `gpt-oss-120b` (120B parameters)\n"
                    "• `qwen-3.2-32b` (Qwen model)\n\n"
                    f"**Fix:**\n"
                    f"1. Go to the sidebar\n"
                    f"2. Select one of the models listed above from the dropdown\n\n"
                    f"Error: {error_msg}"
                )
            
            return f"❌ Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ===================== DISPLAY CHAT HISTORY =====================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===================== CHAT INPUT =====================
if prompt := st.chat_input("Hold to Speak..." if st.session_state.mic_enabled else "Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if web search is needed
    search_keywords = ["search", "google", "find", "look up", "what is", "who is"]
    web_results = None
    if any(keyword in prompt.lower() for keyword in search_keywords):
        if st.session_state.serper_api_key:
            with st.status("🔍 Searching the web...", expanded=False) as status:
                web_results = search_web(prompt)
                if web_results:
                    status.update(label="✅ Web search complete", state="complete")
                else:
                    status.update(label="⚠️ No search results", state="error")
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            response = get_groq_response(prompt, web_results)
            st.markdown(response)
            
            if st.session_state.voice_enabled:
                st.audio("", format="audio/wav")
    
    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# ===================== FOOTER =====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("⚡ Powered by Groq")
with col2:
    st.caption("🔧 Built with Streamlit")
with col3:
    st.caption(f"📝 {len(st.session_state.messages)} messages")

# ===================== AUTO-TEST API KEY =====================
if st.session_state.groq_api_key and not st.session_state.key_tested:
    with st.sidebar:
        with st.status("🔍 Testing API Key...", expanded=False) as status:
            try:
                test_response = get_groq_response("Hello")
                if "Error" not in test_response and "Model" not in test_response:
                    status.update(label="✅ API Key works!", state="complete")
                    st.success("✅ Connection successful!")
                else:
                    status.update(label="⚠️ API Key issue", state="error")
                    st.warning("⚠️ Check model selection or rate limits")
                st.session_state.key_tested = True
            except:
                status.update(label="⚠️ Connection failed", state="error")
                st.session_state.key_tested = True
