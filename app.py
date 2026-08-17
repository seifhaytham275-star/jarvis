import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)

def speak(audio):
    print(f"Jarvis: {audio}")
    engine.say(audio)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-US')
        return query.lower()
    except:
        return "None"

if __name__ == "__main__":
    speak("Welcome home, Sir.")
    while True:
        query = take_command()
        if 'open youtube' in query:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")
        elif 'open instagram' in query:
            speak("Opening Instagram.")
            webbrowser.open("https://www.instagram.com")
        elif 'open google' in query:
            speak("Opening Google.")
            webbrowser.open("https://www.google.com")
        elif 'exit' in query:
            speak("Goodbye, Seif.")
            break
