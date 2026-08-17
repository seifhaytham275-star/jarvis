import datetime
import os
import subprocess
import webbrowser
import pyttsx3
import speech_recognition as sr

# تهيئة محرك الصوت (Text-to-Speech)
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # يمكنك تغيير رقم الصوت حسب المتاح في جهازك

def speak(audio):
    """دالة لجعل جارفيس يتحدث بصوت عالٍ"""
    engine.say(audio)
    engine.runAndWait()

def wish_me():
    """دالة الترحيب بناءً على الوقت الحالي"""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning, Sir.")
    elif 12 <= hour < 18:
        speak("Good afternoon, Sir.")
    else:
        speak("Good evening, Sir.")
    speak("Jarvis Ultimate Pro is online. All systems are fully operational.")

def take_command():
    """دالة للاستماع للأوامر الصوتية من الميكروفون"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 300  # تعديل حساسية الميكروفون إذا لزم الأمر
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query.lower()

if __name__ == "__main__":
    wish_me()
    
    while True:
        query = take_command()

        # الأوامر والوظائف الأساسية لنسخة Ultimate Pro
        
        if 'open youtube' in query:
            speak("Opening YouTube, Sir.")
            webbrowser.open("https://www.youtube.com")

        elif 'open google' in query:
            speak("Opening Google, Sir.")
            webbrowser.open("https://www.google.com")

        elif 'open tiktok' in query:
            speak("Opening TikTok, Sir.")
            webbrowser.open("https://www.tiktok.com")

        elif 'open calendar' in query:
            speak("Opening Calendar, Sir.")
            os.system("start outlookcal:")

        elif 'open calculator' in query:
            speak("Opening Calculator, Sir.")
            os.system("calc")

        elif 'open notepad' in query:
            speak("Opening Notepad, Sir.")
            os.system("notepad")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'exit' in query or 'quit' in query or 'shutdown' in query:
            speak("Shutting down systems. Goodbye, Sir.")
            break
