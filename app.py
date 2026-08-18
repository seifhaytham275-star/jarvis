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
    st.session_state.model_name = "llama-3.1-8b-instant"
if 'key_tested' not in st.session_state:
    st.session_state.key_tested = False

# ===================== SIDEBAR =====================
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    st.subheader("🔑 API Keys")
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        value=st.session_state.groq_api_key,
        help="Get your free key from console.groq.com"
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
    
    if st.session_state.groq_api_key:
        st.success("✅ Groq API Key set")
    else:
        st.warning("⚠️ Groq API Key required")
    
    st.divider()
    
    st.subheader("🧠 Model Selection")
    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama-4-scout-17b-16e-instruct",
        "qwen-3.2-32b",
        "openai/gpt-oss-120b",
    ]
    
    selected_model = st.selectbox(
        "Select Model",
        options=model_options,
        index=0,
        help="'llama-3.1-8b-instant' works on all free accounts"
    )
    
    if selected_model:
        st.session_state.model_name = selected_model
        st.info(f"🧠 Using: {selected_model}")
    
    st.divider()
    
    st.subheader("🎛️ Features")
    st.session_state.voice_enabled = st.toggle("🔊 Voice Response", value=st.session_state.voice_enabled)
    st.session_state.mic_enabled = st.toggle("🎤 Microphone", value=st.session_state.mic_enabled)
    st.session_state.arabic_mix = st.toggle("🌍 Mix Eloquent/Slang Arabic", value=st.session_state.arabic_mix)
    
    st.divider()
    
    st.subheader("📜 Chat History")
    if st.session_state.messages:
        for msg in st.session_state.messages[-5:]:
            if msg["role"] == "user":
                st.caption(f"👤 {msg['content'][:25]}...")
    else:
        st.caption("No messages yet")
    
    st.divider()
    
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
    st.caption(f"🟢 Status: {'Ready' if st.session_state.groq_api_key else 'No API Key'}")
    st.caption(f"📡 Model: {st.session_state.model_name}")
    st.caption(f"💬 Messages: {len(st.session_state.messages)}")

# ===================== MAIN =====================
st.title("🤖 J.A.R.V.I.S. Prime")
st.caption("At your command, Sir...")

def search_web(query):
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

def get_available_models():
    if not st.session_state.groq_api_key:
        return None
    
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {st.session_state.groq_api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            return [m.get("id", "") for m in models]
        return None
    except:
        return None

def get_groq_response(prompt, web_results=None):
    if not st.session_state.groq_api_key:
        return "⚠️ Please enter your Groq API Key in the sidebar."
    
    full_prompt = prompt
    if web_results:
        full_prompt = f"{prompt}\n\n🔍 Web Search Results:\n{web_results}"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.session_state.groq_api_key}",
        "Content-Type": "application/json"
    }
    
    system_msg = "You are J.A.R.V.I.S., Tony Stark's AI assistant. Be helpful, witty, and professional."
    if st.session_state.arabic_mix:
        system_msg += " Mix eloquent Arabic with English and some slang Arabic when appropriate."
    
    messages = [{"role": "system", "content": system_msg}]
    for msg in st.session_state.messages[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": full_prompt})
    
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
            
            available = get_available_models()
            if available:
                models_list = "\n".join([f"  • `{m}`" for m in available[:10]])
                return (
                    f"❌ Error: {error_msg}\n\n"
                    f"**Available models for your API key:**\n{models_list}\n\n"
                    f"**Fix:** Select a model from the dropdown that's in the list above."
                )
            else:
                return f"❌ Error: {error_msg}\n\n**Fix:** Make sure your API key is valid and starts with 'gsk_'"
            
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ===================== DISPLAY CHAT =====================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===================== CHAT INPUT =====================
if prompt := st.chat_input("Hold to Speak..." if st.session_state.mic_enabled else "Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
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
    
    with st.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            response = get_groq_response(prompt, web_results)
            st.markdown(response)
            if st.session_state.voice_enabled:
                st.audio("", format="audio/wav")
    
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

# ===================== AUTO-TEST =====================
if st.session_state.groq_api_key and not st.session_state.key_tested:
    with st.sidebar:
        with st.status("🔍 Testing API Key...", expanded=False) as status:
            try:
                test_response = get_groq_response("Hello")
                if "Error" not in test_response:
                    status.update(label="✅ API Key works!", state="complete")
                    st.success("✅ Connection successful!")
                else:
                    status.update(label="⚠️ API Key issue", state="error")
                    st.warning("⚠️ Check your API key or model selection")
                st.session_state.key_tested = True
            except Exception as e:
                status.update(label="⚠️ Connection failed", state="error")
                st.error(f"Error: {str(e)}")
                st.session_state.key_tested = True
