import os
import io
import streamlit as st
from PIL import Image
import requests
from gtts import gTTS
from groq import Groq
from googlesearch import search
import chromadb
from sentence_transformers import SentenceTransformer
from audio_recorder_streamlit import audio_recorder

# Page Configuration
st.set_page_config(
    page_title="Jarvis Ultimate AI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Jarvis Ultimate Assistant")
st.write("System Status: All Modules Active (Voice, Vision, Search, Memory, TTS)")

# Sidebar Configuration
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Initialize Local Memory (ChromaDB + Sentence Transformers)
@st.cache_resource
def init_memory():
    chroma_client = chromadb.PersistentClient(path="./jarvis_vector_db")
    col = chroma_client.get_or_create_collection(name="jarvis_memory")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return col, model

collection, embedder = init_memory()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MODULE 1: PIL (Pillow) - Image Uploader ---
st.sidebar.subheader("Vision Module")
uploaded_file = st.sidebar.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
image_desc = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption=f"Loaded ({image.size[0]}x{image.size[1]})", use_column_width=True)
    image_desc = "[User has provided an image for analysis]"

# --- MODULE 2: Audio Recorder & Groq Whisper ---
st.sidebar.subheader("Voice Input Module")
audio_bytes = audio_recorder(text="Click to Record Voice", icon_size="2x", icon_name="microphone")

prompt = None
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    if groq_api_key:
        with st.spinner("Transcribing audio with Groq Whisper..."):
            try:
                client = Groq(api_key=groq_api_key)
                with open("temp_voice.wav", "wb") as f:
                    f.write(audio_bytes)
                with open("temp_voice.wav", "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=("temp_voice.wav", file.read()),
                        model="whisper-large-v3",
                    )
                    prompt = transcription.text
                    st.success(f"Recognized: {prompt}")
            except Exception as e:
                st.error(f"Transcription error: {e}")

# Text input fallback
text_prompt = st.chat_input("Type your message to Jarvis...")
if text_prompt:
    prompt = text_prompt

# Main Logic Execution
if prompt:
    if not groq_api_key:
        st.warning("Please enter your Groq API Key in the sidebar settings.")
    else:
        full_user_input = f"{prompt} {image_desc}"
        st.session_state.messages.append({"role": "user", "content": full_user_input})
        with st.chat_message("user"):
            st.markdown(full_user_input)

        # --- MODULE 3: Google Search + Requests (Web Scraping) ---
        enhanced_prompt = full_user_input
        if "search" in prompt.lower() or "بحث" in prompt or "news" in prompt.lower():
            with st.status("Searching Google & scraping web data...", expanded=False):
                try:
                    urls = []
                    for url in search(prompt, num_results=2):
                        urls.append(url)
                    
                    scraped_data = ""
                    if urls:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        resp = requests.get(urls[0], headers=headers, timeout=5)
                        scraped_data = resp.text[:1000]
                        
                    enhanced_prompt = f"User Query: {prompt}\nWeb Links: {urls}\nWeb Page Content: {scraped_data}"
                except Exception as e:
                    enhanced_prompt = f"User Query: {prompt}\nSearch Error: {e}"

        # --- MODULE 4: ChromaDB & Sentence-Transformers (Memory Retrieval) ---
        try:
            query_embedding = embedder.encode([prompt]).tolist()[0]
            results = collection.query(query_embeddings=[query_embedding], n_results=2)
            memories = results['documents'][0] if results['documents'] else []
            memory_context = f"\nRelevant Past Memories: {memories}" if memories else ""
        except Exception:
            memory_context = ""

        try:
            client = Groq(api_key=groq_api_key)
            
            chat_history = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages[:-1]
            ]
            
            system_message = {
                "role": "system",
                "content": (
                    "You are Jarvis, an advanced AI assistant. Fluent in all languages. "
                    "Avoid mixing random Chinese characters or strange glyphs. Respond cleanly and accurately. "
                    f"{memory_context}"
                )
            }
            
            messages_payload = [system_message] + chat_history + [{"role": "user", "content": enhanced_prompt}]

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
            )
            
            response_text = completion.choices[0].message.content

            # Save interaction to ChromaDB Memory
            try:
                doc_id = str(len(collection.get()['ids']) + 1)
                emb = embedder.encode([f"Q: {prompt} A: {response_text}"]).tolist()[0]
                collection.add(documents=[f"Q: {prompt} A: {response_text}"], embeddings=[emb], ids=[doc_id])
            except Exception:
                pass

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

                # --- MODULE 5: gTTS (Text-to-Speech Output) ---
                try:
                    tts = gTTS(text=response_text[:400], lang='en', slow=False)
                    tts.save("response.mp3")
                    st.audio("response.mp3", format="audio/mp3")
                except Exception:
                    pass
                
        except Exception as e:
            st.error(f"Error connecting to Groq: {e}")
