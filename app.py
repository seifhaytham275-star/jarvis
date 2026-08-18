import os
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
if 'cerebras_api_key' not in st.session_state:
    st.session_state.cerebras_api_key = ""
if 'serper_api_key' not in st.session_state:
    st.session_state.serper_api_key = ""
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False
if 'mic_enabled' not in st.session_state:
    st.session_state.mic_enabled = False
if 'arabic_mix' not in st.session_state:
    st.session_state.arabic_mix = False

# ===================== SIDEBAR - API KEYS & SETTINGS =====================
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # ===== API KEYS SECTION =====
    st.subheader("🔑 API Keys")
    
    # Cerebras API Key
    cerebras_key = st.text_input(
        "Cerebras API Key",
        type="password",
        placeholder="csk-...",
        value=st.session_state.cerebras_api_key,
        help="Get your key from cloud.cerebras.ai"
    )
    if cerebras_key:
        st.session_state.cerebras_api_key = cerebras_key
    
    # Serper API Key
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        placeholder="Enter Serper API key...",
        value=st.session_state.serper_api_key,
        help="Get your key from serper.dev"
    )
    if serper_key:
        st.session_state.serper_api_key = serper_key
    
    # Show API Key Status
    if st.session_state.cerebras_api_key:
        st.success("✅ Cerebras API Key set")
    else:
        st.warning("⚠️ Cerebras API Key required")
    
    if st.session_state.serper_api_key:
        st.success("✅ Serper API Key set")
    else:
        st.info("ℹ️ Serper API Key optional (for web search)")
    
    st.divider()
    
    # ===== FEATURES SECTION =====
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
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.messages = []
            st.session_state.cerebras_api_key = ""
            st.session_state.serper_api_key = ""
            st.rerun()
    
    st.divider()
    
    # ===== STATUS =====
    st.caption(f"🟢 Status: {'Ready' if st.session_state.cerebras_api_key else 'No API Key'}")

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

def get_cerebras_response(prompt, web_results=None):
    """Get response from Cerebras API"""
    if not st.session_state.cerebras_api_key:
        return "⚠️ Please enter your Cerebras API Key in the sidebar."
    
    # Prepare the prompt with web results if available
    full_prompt = prompt
    if web_results:
        full_prompt = f"{prompt}\n\n🔍 Web Search Results:\n{web_results}"
    
    url = "https://api.cerebras.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {st.session_state.cerebras_api_key}",
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
    
    # ===== FIX: Use correct model name =====
    # OPTIONS: "llama3.1-8b", "llama3.1-70b", "llama3-8b", "llama3-70b"
    payload = {
        "model": "llama3.1-8b",  # ← CHANGE THIS if needed
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
            
            # Handle model not found error
            if "model_not_found" in error_msg or "404" in str(response.status_code):
                return (
                    "❌ **Model Not Found Error**\n\n"
                    "The model 'llama3.1-8b' is not available.\n\n"
                    "**Fix:**\n"
                    "1. Go to cloud.cerebras.ai to see your available models\n"
                    "2. Change the 'model' name in the code (line ~107)\n"
                    "3. Try: 'llama3-8b', 'llama3.1-70b', or 'llama3-70b'\n\n"
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
            response = get_cerebras_response(prompt, web_results)
            st.markdown(response)
            
            # Voice output placeholder
            if st.session_state.voice_enabled:
                st.audio("", format="audio/wav")  # Placeholder for TTS
    
    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# ===================== FOOTER =====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("⚡ Powered by Cerebras AI")
with col2:
    st.caption("🔧 Built with Streamlit")
with col3:
    st.caption(f"📝 {len(st.session_state.messages)} messages")

# ===================== AUTO-TEST API KEY =====================
if st.session_state.cerebras_api_key and "key_tested" not in st.session_state:
    with st.sidebar:
        with st.status("🔍 Testing API Key...", expanded=False):
            test_response = get_cerebras_response("Hello")
            if "Error" not in test_response and "Model" not in test_response:
                st.success("✅ API Key works!")
            else:
                st.error("⚠️ API Key issue - check model name")
            st.session_state.key_tested = True
