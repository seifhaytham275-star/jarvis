import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Authentication View (Login Screen)
if not st.session_state.logged_in:
    st.title("🔐 Jarvis Security Access")
    st.write("Please enter your passcode to unlock the system, Sir.")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect passcode. Please try again, Sir.")

# Main Dashboard View (Post-Authentication)
else:
    # Sidebar Settings
    st.sidebar.title("⚙️ Jarvis Settings")
    st.sidebar.write("Configure your system preferences.")
    
    # Comprehensive World Languages List
    world_languages = [
        "Arabic (العربية)",
        "English",
        "Spanish (Español)",
        "French (Français)",
        "German (Deutsch)",
        "Chinese (中文)",
        "Japanese (日本語)",
        "Russian (Русский)",
        "Portuguese (Português)",
        "Italian (Italiano)",
        "Hindi (हिन्दी)",
        "Korean (한국어)",
        "Turkish (Türkçe)",
        "Urdu (اردو)",
        "Persian (فارسی)",
        "Dutch (Nederlands)",
        "Greek (Ελληνικά)",
        "Hebrew (עברית)",
        "Indonesian (Bahasa Indonesia)",
        "Malay (Bahasa Melayu)",
        "Polish (Polski)",
        "Romanian (Română)",
        "Swedish (Svenska)",
        "Thai (ไทย)",
        "Vietnamese (Tiếng Việt)",
        "Ukrainian (Українська)"
    ]
    
    selected_language = st.sidebar.selectbox("Select System Language", world_languages)
    
    # API Key Configuration
    api_key_input = st.sidebar.text_input("Enter Gemini API Key", type="password")
    
    st.sidebar.divider()
    if st.sidebar.button("Lock System"):
        st.session_state.logged_in = False
        st.rerun()

    # Main Dashboard Header
    st.title("🤖 Jarvis AI Assistant Dashboard")
    st.success("Welcome home, Sir!")
    st.write(f"System Status: **Online & Operational** | Active Language: **{selected_language}**")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input box
    if prompt := st.chat_input("Type your message to Jarvis..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if api_key_input:
                try:
                    genai.configure(api_key=api_key_input)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    reply = response.text
                except Exception as e:
                    reply = f"Error connecting to AI model: {e}"
            else:
                reply = f"Jarvis received your command: '{prompt}'. (Please enter your Gemini API Key in the sidebar settings to get live AI intelligence responses)."
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
