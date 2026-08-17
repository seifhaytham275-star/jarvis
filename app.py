import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state for authentication persistence
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Authentication View (Login Screen)
if not st.session_state.logged_in:
    st.title("🔐 Jarvis Security Access")
    st.write("Please enter your passcode to unlock the system.")
    
    # Password input field with hidden characters
    password = st.text_input("Password", type="password")
    
    # Login trigger button
    if st.button("Login"):
        if password == "123":
            st.session_state.logged_in = True
            st.rerun()  # Refresh the page to load the main dashboard
        else:
            st.error("Incorrect passcode. Please try again, Sir.")

# Main Dashboard View (Post-Authentication)
else:
    st.title("🤖 Jarvis AI Assistant Dashboard")
    st.success("Welcome home, Sir!")
    
    st.write("System Status: **Online & Operational**")
    
    # User interaction area for chatting or entering commands
    user_input = st.text_input("Enter your command or message:")
    
    if st.button("Send"):
        if user_input:
            st.write(f"**Jarvis:** Processing command -> *{user_input}*")
        else:
            st.warning("Please type something before sending.")
            
    st.divider()
    
    # Logout / Lock system button
    if st.button("Lock System"):
        st.session_state.logged_in = False
        st.rerun()
