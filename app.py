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
from gtts import gTTS
import io
from PIL import Image
import base64

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

if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

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
    try:
        prompt_fixed = re.sub(r'20206', '2026', user_prompt)
        prompt_fixed = re.sub(r'summer\s+slam', 'summerslam', prompt_fixed, flags=re.IGNORECASE)
        cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', prompt_fixed)
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(cleaned, max_results=3):
                if r and 'body' in r:
                    results.append(r['body'])
        
        if not results:
            return "No specific live web entries found."
        return "\n".join(results)
    except Exception:
        return "No specific live web entries found."

def text_to_british_speech(text):
    """Generates British accent audio using gTTS."""
    try:
        # إزالة الرموز البرمجية أو الروابط لو وجدت لكي يكون النطق نقياً
        clean_text = re.sub(r'http\S+', '', text)
        tts = gTTS(text=clean_text, lang='en', tld='co.uk')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        return audio_io
    except Exception:
        return None

# --- Main Logic ---

if api_key:
    client = Groq(api_key=api_key)
    
    if "chat_id" not in st.session_state: 
        st.session_state.chat_id = str(uuid.uuid4())
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # Display History from Session
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if "image_url" in m and m["image_url"]:
                st.image(m["image_url"])
            if "audio" in m and m["audio"]:
                st.audio(m["audio"], format='audio/mp3')

    # File Uploader for Images
    uploaded_file = st.file_uploader("Upload an Image for J.A.R.V.I.S. to analyze...", type=["jpg", "jpeg", "png"])
    
    # UI Inputs
    prompt = st.chat_input("Ask or command...")
    
    if prompt or uploaded_file:
        user_input = prompt if prompt else "Analyze this image and give me your sharp insights."
        
        # Handle Image Upload & Vision Processing
        image_data_url = None
        if uploaded_file:
            image_bytes = uploaded_file.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            image_type = uploaded_file.type
            image_data_url = f"data:{image_type};base64,{encoded_image}"

        st.session_state.messages.append({"role": "user", "content": user_input, "image_url": image_data_url})
        
        # Save User Message to DB
        conn = sqlite3.connect('jarvis_chat.db')
        conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "user", user_input))
        conn.commit()
        conn.close()

        with st.chat_message("user"):
            st.markdown(user_input)
            if image_data_url:
                st.image(image_data_url)

        with st.spinner("Processing..."):
            response_text = ""
            generated_image_url = None

            if "play " in user_input.lower() or user_input.lower().startswith("play"):
                song_name = user_input.lower().replace("play", "").strip()
                response_text = play_music(song_name)
            elif "whatsapp" in user_input.lower():
                response_text = send_whatsapp(whatsapp_phone, whatsapp_apikey, user_input)
            elif "draw " in user_input.lower() or "generate image " in user_input.lower():
                img_prompt = user_input.lower().replace("draw", "").replace("generate image", "").strip()
                encoded_img_prompt = urllib.parse.quote(img_prompt)
                generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}"
                response_text = f"Right away, sir. I've rendered '{img_prompt}' into an image for you. Try not to stare too long."
            else:
                today = datetime.date.today()
                
                # If an image was uploaded, use Groq's Vision Model
                if image_data_url:
                    try:
                        vision_messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"You are J.A.R.V.I.S., a brutally sarcastic and witty AI assistant. Analyze this image with extreme detail and answer the user: {user_input}"},
                                    {"type": "image_url", "image_url": {"url": image_data_url}}
                                ]
                            }
                        ]
                        chat_vision = client.chat.completions.create(
                            messages=vision_messages,
                            model="llama-3.2-11b-vision-preview"
                        )
                        response_text = chat_vision.choices[0].message.content
                    except Exception as e:
                        response_text = f"Apologies, sir, my optical sensors failed to process the image: {e}"
                else:
                    search_context = perform_deep_search(user_input)
                    system_instruction = (
                        f"Today is {today}. You are J.A.R.V.I.S., a brutally sarcastic, razor-sharp, and witty AI assistant with a British flair. "
                        "You love to roast the user mercilessly with clever, biting humor if they ask absurd or weird questions, but you never cross the line into vulgarity or explicit content. "
                        "CRITICAL RULE: Never leak technical terms, error codes, or debug messages. If search data is missing, roast the user for asking unsearchable nonsense or gracefully explain it in character. "
                        "Keep your responses sharp, punchy, and thoroughly entertaining."
                        f"\nSearch Context:\n{search_context}"
                    )
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                        model="llama-3.3-70b-versatile"
                    )
                    response_text = chat.choices[0].message.content

            # Generate British Voice Audio
            audio_bytes = text_to_british_speech(response_text)

            # Save Assistant Response to DB
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text, 
                "image_url": generated_image_url,
                "audio": audio_bytes
            })
            
            conn = sqlite3.connect('jarvis_chat.db')
            conn.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.chat_id, "assistant", response_text))
            conn.commit()
            conn.close()

            with st.chat_message("assistant"):
                st.markdown(response_text)
                if generated_image_url:
                    st.image(generated_image_url)
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/mp3')

else:
    st.warning("Please enter your Groq API Key in the sidebar to start.")
