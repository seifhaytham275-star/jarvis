import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import datetime
import urllib.parse
import urllib.request
import webbrowser
import sqlite3
import uuid
import re

# --- Database Setup (Chat History) ---
def init_db():
    conn = sqlite3.connect('jarvis_chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (chat_id TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_history(chat_id):
    conn = sqlite3.connect('jarvis_chat.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE chat_id=?", (chat_id,))
    data = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in data]

def get_all_chats():
    conn = sqlite3.connect('jarvis_chat.db')
    c = conn.cursor()
    c.execute('''
        SELECT chat_id, content 
        FROM messages 
        WHERE role='user' 
        GROUP BY chat_id 
        ORDER BY rowid DESC
    ''')
    chats = c.fetchall()
    conn.close()
    return chats

# --- Page Configuration ---
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. AI Assistant")

# --- Sidebar Inputs & Recent Chats ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("WhatsApp Settings")
whatsapp_phone = st.sidebar.text_input("Target Phone Number (e.g., +20...)")
whatsapp_apikey = st.sidebar.text_input("CallMeBot API Key")

st.sidebar.markdown("---")
st.sidebar.subheader("Recent Chats (المحادثات السابقة)")

# زر محادثة جديدة
if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

# عرض المحادثات السابقة في السيدبار
chats = get_all_chats()
for chat_id, first_msg in chats:
    title = first_msg[:22] + "..." if len(first_msg) > 22 else first_msg
    if st.sidebar.button(f"💬 {title}", key=chat_id):
        st.session_state.chat_id = chat_id
        st.session_state.messages = get_history(chat_id)
        st.rerun()

# --- Utility Functions ---

def play_music(song):
    query = urllib.parse.quote(song)
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={query}")
    return f"Oh brilliant, I've queued up '{song}' on YouTube just for you. Try not to break your speakers."

def send_whatsapp(phone, apikey, message):
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={apikey}"
        with urllib.request.urlopen(url) as response:
            return "WhatsApp message sent successfully. Happy now?" if response.status == 200 else "Failed to send WhatsApp message."
    except Exception as e:
        return f"WhatsApp error: {e}"

def perform_deep_search(user_prompt):
    """Clean search without fake fallbacks to prevent model hallucinations."""
    try:
        prompt_fixed = re.sub(r'20206', '2026', user_prompt)
        prompt_fixed = re.sub(r'2026\d+', '2026', prompt_fixed)
        
        cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', prompt_fixed)
        cleaned = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', cleaned)
        cleaned = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', cleaned)
        
        results = []
        with DDGS() as ddgs:
            queries = [cleaned, f"{cleaned} wwe results match card"]
            for q in queries:
                for r in ddgs.text(q, max_results=3):
                    if 'body' in r:
                        results.append(r['body'])
        
        if not results:
            return "NO_SEARCH_RESULTS_FOUND"
        return "\n".join(list(set(results))[:5])
    except Exception:
        return "NO_SEARCH_RESULTS_FOUND"

# --- Main Logic ---

if api_key:
    client = Groq(api_key=api_key)
    
    # Initialize Session
    if "chat_id" not in st.session_state: 
        st.session_state.chat_id = str(uuid.uuid4())
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # Display History from Session
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # UI Inputs
    prompt = st.chat_input("Ask or command...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Save User Message to DB
        conn = sqlite3.connect('jarvis_chat.db')
        conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "user", prompt))
        conn.commit()
        conn.close()

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Processing..."):
            response_text = ""

            if "play " in prompt.lower() or prompt.lower().startswith("play"):
                song_name = prompt.lower().replace("play", "").strip()
                response_text = play_music(song_name)
            elif "whatsapp" in prompt.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, prompt)
            else:
                today = datetime.date.today()
                search_context = perform_deep_search(prompt)
                
                system_instruction = (
                    f"Today is {today}. You are J.A.R.V.I.S., a sarcastic, witty, highly intelligent AI assistant. "
                    "You love to roast the user with mild humor, but you must be 100% truthful. "
                    "CRITICAL ANTI-HALLUCINATION RULE: If the Search Context below says 'NO_SEARCH_RESULTS_FOUND' or lacks exact details about the event, "
                    "DO NOT invent matches, wrestlers, or outcomes. Admit clearly and sarcastically that you don't have the live data for it right now, "
                    "instead of making things up. If valid search context exists, summarize it accurately."
                    f"\nSearch Context:\n{search_context}"
                )
                
                chat = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                    model="llama-3.3-70b-versatile"
                )
                response_text = chat.choices[0].message.content

            # Save Assistant Response to DB
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            conn = sqlite3.connect('jarvis_chat.db')
            conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "assistant", response_text))
            conn.commit()
            conn.close()

            with st.chat_message("assistant"):
                st.markdown(response_text)

else:
    st.warning("Please enter your Groq API Key in the sidebar to start.")
