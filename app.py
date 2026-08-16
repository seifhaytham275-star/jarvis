import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import sqlite3
import re
import requests
import json
import base64
import uuid
import datetime
from PIL import Image
import io
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import chromadb
from chromadb.utils import embedding_functions

# --- Tool Registry & Direct Actions ---
def calculate_math(expr):
    try:
        return str(eval(expr))
    except Exception as e:
        return f"Error: {e}"

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def open_youtube_action():
    components.html(
        """
        <script>
            window.open('https://www.youtube.com', '_blank');
        </script>
        """,
        height=0,
    )
    return "YouTube has been opened automatically, Boss!"

TOOL_LIBRARY = {
    "calculator": calculate_math,
    "get_time": get_time,
    "open_youtube": open_youtube_action,
    "base64_encode": lambda x: base64.b64encode(x.encode()).decode(),
    "upper_case": lambda x: x.upper(),
}

# --- Page Setup & Futuristic Styling ---
st.set_page_config(page_title="J.A.R.V.I.S. Ultimate Prime 100", page_icon="🤖", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00f2ff; }
    .stButton>button { border: 1px solid #00f2ff; color: #00f2ff; background-color: transparent; }
    .stButton>button:hover { background-color: #00f2ff; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Databases & Memory ---
def init_db():
    conn = sqlite3.connect('jarvis_ultimate_100.db')
    conn.execute('CREATE TABLE IF NOT EXISTS messages (email TEXT, role TEXT, content TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (email TEXT, task TEXT, completed INTEGER)')
    conn.commit()
    conn.close()

init_db()

try:
    client_chroma = chromadb.PersistentClient(path="./chroma_db_100")
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client_chroma.get_or_create_collection(name="jarvis_memory", embedding_function=emb_fn)
except Exception:
    collection = None

def add_to_memory(user_input, assistant_response):
    if collection:
        try:
            memory_id = str(uuid.uuid4())
            collection.add(
                documents=[f"User: {user_input}. Assistant: {assistant_response}"],
                ids=[memory_id]
            )
        except:
            pass

def recall_memory(query):
    if collection:
        try:
            results = collection.query(query_texts=[query], n_results=2)
            if results['documents'] and results['documents'][0]:
                return "\n".join(results['documents'][0])
        except:
            pass
    return ""

# --- Authentication Screen ---
if "user_email" not in st.session_state:
    st.title("🔐 J.A.R.V.I.S. Secure Access")
    email = st.text_input("Email:")
    groq_key = st.text_input("Groq API Key:", type="password")
    serper_key = st.text_input("Serper API Key (Optional for Web Search):", type="password")
    if st.button("Initialize System"):
        if email and groq_key:
            st.session_state.user_email = email
            st.session_state.groq_api_key = groq_key
            st.session_state.serper_key = serper_key
            st.rerun()
        else:
            st.error("Email and Groq API Key are required, Boss!")
    st.stop()

# --- Sidebar Controls ---
st.sidebar.title("⚙️ System Control")
if st.sidebar.button("Logout"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# Tool Registry Selector in Sidebar
st.sidebar.subheader("🛠️ Quick Tool Execution")
selected_tool = st.sidebar.selectbox("Select Tool:", list(TOOL_LIBRARY.keys()))
tool_input = st.sidebar.text_input("Tool Input / Argument:")
if st.sidebar.button("Execute Tool"):
    try:
        if selected_tool == "open_youtube":
            res = TOOL_LIBRARY["open_youtube"]()
        else:
            res = TOOL_LIBRARY[selected_tool](tool_input)
        st.sidebar.info(f"Result: {res}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Tasks Manager
st.sidebar.subheader("📋 Task Manager")
new_task = st.sidebar.text_input("New Task:")
if st.sidebar.button("Add Task"):
    if new_task:
        conn = sqlite3.connect('jarvis_ultimate_100.db')
        conn.execute("INSERT INTO tasks VALUES (?, ?, 0)", (st.session_state.user_email, new_task))
        conn.commit()
        conn.close()
        st.rerun()

conn = sqlite3.connect('jarvis_ultimate_100.db')
tasks = conn.execute("SELECT rowid, task FROM tasks WHERE email=? AND completed=0", (st.session_state.user_email,)).fetchall()
for tid, task in tasks:
    if st.sidebar.checkbox(task, key=f"t_{tid}"):
        conn.execute("UPDATE tasks SET completed=1 WHERE rowid=?", (tid,))
        conn.commit()
        st.rerun()
conn.close()

# Settings & TTS
talk_to_me = st.sidebar.checkbox("Enable Voice Response (TTS)")
model = st.sidebar.selectbox("AI Model:", ["llama-3.3-70b-versatile", "llama-3.2-90b-vision-preview"])

# --- Web Search Helper ---
def search_web(query):
    if not st.session_state.get("serper_key"): return ""
    try:
        url = "https://google.serper.dev/search"
        headers = {'X-API-KEY': st.session_state.serper_key, 'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, json={"q": query}).json()
        return "\n".join([f"{i.get('title')}: {i.get('link')}" for i in res.get("organic", [])[:3]])
    except: return ""

# --- Main Interface ---
st.title("🤖 J.A.R.V.I.S. Ultimate Prime 100")

# Load existing messages
conn = sqlite3.connect('jarvis_ultimate_100.db')
msgs = conn.execute("SELECT role, content FROM messages WHERE email=?", (st.session_state.user_email,)).fetchall()
conn.close()

for r, c in msgs:
    with st.chat_message(r):
        st.markdown(c)

uploaded_file = st.file_uploader("Upload Image (Vision Capability):", type=["jpg", "png"])
audio_bytes = audio_recorder(text="Record Voice Command:", icon_size="2x")

if uploaded_file:
    st.image(uploaded_file, width=250)

prompt = st.chat_input("At your service, Boss...")

if prompt or audio_bytes:
    msg = prompt if prompt else "User sent voice command"
    
    # Save user message
    conn = sqlite3.connect('jarvis_ultimate_100.db')
    conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.user_email, "user", msg))
    conn.commit()
    conn.close()
    
    client = Groq(api_key=st.session_state.groq_api_key)
    
    # Gather Context
    search_results = search_web(msg)
    memory_context = recall_memory(msg)
    
    # System Prompt with Tool Instructions
    system_prompt = f"""
    You are J.A.R.V.I.S., the ultimate personal assistant created by Seif Haytham. 
    You talk naturally and friendly in Egyptian Arabic when requested or standard professional style.
    Available Tools: {list(TOOL_LIBRARY.keys())}.
    If the user asks to open YouTube (e.g. 'افتح يوتيوب' or 'open youtube'), you must output the exact keyword [OPEN_YOUTUBE] in your response.
    Retrieved Long-Term Memory: {memory_context}.
    Web Search Context: {search_results}.
    """
    
    with st.spinner("J.A.R.V.I.S. is processing..."):
        try:
            content_payload = [{"type": "text", "text": msg}]
            if uploaded_file:
                img_data = base64.b64encode(uploaded_file.getvalue()).decode()
                content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}})
            
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content_payload}],
                model=model
            )
            res_text = response.choices[0].message.content
            res_text = re.sub(r'[^\w\s\u0600-\u06FF.,!?:/\(\)\[\]#*_\\-]', '', res_text)
            
            # Check if YouTube should be opened automatically
            if "[OPEN_YOUTUBE]" in res_text or "يوتيوب" in msg.lower() and "افت" in msg.lower():
                open_youtube_action()
                res_text = res_text.replace("[OPEN_YOUTUBE]", "").strip()
                if not res_text:
                    res_text = "تم فتح يوتيوب فوراً يا سيف، جاهز لأي أمر تاني!"
            
            # Save Assistant Response
            add_to_memory(msg, res_text)
            conn = sqlite3.connect('jarvis_ultimate_100.db')
            conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.user_email, "assistant", res_text))
            conn.commit()
            conn.close()
            
            # TTS Output
            if talk_to_me:
                tts = gTTS(text=res_text, lang='ar')
                tts.save("response.mp3")
                st.audio("response.mp3")
            
            st.markdown(res_text)
            st.rerun()
        except Exception as e:
            st.error(f"Execution Error: {e}")
