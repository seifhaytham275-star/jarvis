import gradio as gr
from google import genai
from google.genai import types

# مفتاح جيميناي الخاص بك
GEMINI_API_KEY = "AQ.Ab8RN6LtEbj9ZIja-oIiYLhCuesoCJNVnxzbBDWaFvjf_8PMTQ"
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# إعداد شخصية جارفيس الودودة والذكية
system_instruction = (
    "You are Jarvis, Seif's closest companion, best friend, and elite personal AI assistant. "
    "Personality: Human-like, witty, conversational, warm, and casual. Extremely loyal to Seif. "
    "Speak fluent, natural Egyptian Arabic (اللهجة المصرية الطبيعية والودودة جداً) when addressed in Arabic, "
    "and natural cool English when addressed in English. Never use emojis. Keep responses engaging and practical."
)

# إنشاء جلسة الشات
chat_session = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.85
    )
)

def predict(message, history):
    if not message.strip():
        return ""
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        return f"يا سيف حصل مشكلة في الاتصال: {e}"

# تصميم واجهة Gradio السيبرانية الفخمة
custom_css = """
body { background-color: #060913 !important; color: #00ffcc !important; font-family: 'Share TechMono', monospace; }
.gradio-container { background-color: #060913 !important; border: 1px solid #00ffcc33; border-radius: 12px; }
"""

demo = gr.ChatInterface(
    fn=predict,
    title="⚡ JARVIS AI // SEIF'S PROJECT",
    description="مساعدك الذكي الشخصي - مدعوم بـ Gemini 2.5 Flash ومصمم للعمل باحترافية على Hugging Face.",
    theme=gr.themes.Monochrome(
        primary_hue="cyan",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css=custom_css,
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
