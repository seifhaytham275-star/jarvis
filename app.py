import datetime
import os
import webbrowser
import tkinter as tk
from tkinter import END, Entry, Text

# إعداد نافذة الشات لنسخة Ultimate Pro ChatBox
root = tk.Tk()
root.title("Jarvis Ultimate Pro - ChatBox Edition")
root.geometry("450x550")
root.config(bg="#1e1e1e")
root.resizable(False, False)


def send_message(event=None):
  query = entry_box.get().strip()
  if not query:
    return

  # عرض رسالة المستخدم في الشات
  chat_log.config(state=tk.NORMAL)
  chat_log.insert(END, f"You: {query}\n")

  # معالجة الأوامر بنظام Ultimate Pro
  response = process_command(query.lower())
  chat_log.insert(END, f"Jarvis: {response}\n\n")

  chat_log.config(state=tk.DISABLED)
  chat_log.yview(END)
  entry_box.delete(0, END)


def process_command(query):
  if "open youtube" in query or "يوتيوب" in query:
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube, Sir."

  elif "open google" in query or "جوجل" in query:
    webbrowser.open("https://www.google.com")
    return "Opening Google, Sir."

  elif "open tiktok" in query or "تيك توك" in query:
    webbrowser.open("https://www.tiktok.com")
    return "Opening TikTok, Sir."

  elif "open calendar" in query or "كالندر" in query:
    os.system("start outlookcal:")
    return "Opening Calendar, Sir."

  elif "open calculator" in query or "حاسبة" in query:
    os.system("calc")
    return "Opening Calculator, Sir."

  elif "open notepad" in query or "نوت باد" in query:
    os.system("notepad")
    return "Opening Notepad, Sir."

  elif "time" in query or "الوقت" in query:
    str_time = datetime.datetime.now().strftime("%H:%M:%S")
    return f"Sir, the time is {str_time}"

  elif "hello" in query or "hi" in query:
    return "Jarvis Ultimate Pro ChatBox is online. All systems operational, Sir."

  else:
    return f"Command '{query}' processed successfully, Sir."


# شاشة عرض المحادثة
chat_log = Text(
    root, bg="#2d2d2d", fg="#00ffcc", font=("Consolas", 11), wrap=tk.WORD
)
chat_log.place(x=10, y=10, width=430, height=460)
chat_log.config(state=tk.DISABLED)

# خانة كتابة الرسالة
entry_box = Entry(root, bg="#3d3d3d", fg="#ffffff", font=("Consolas", 12))
entry_box.place(x=10, y=485, width=330, height=40)
entry_box.bind("<Return>", send_message)
entry_box.focus()

# زر الإرسال
send_btn = tk.Button(
    root,
    text="Send",
    bg="#007acc",
    fg="#ffffff",
    font=("Consolas", 10, "bold"),
    command=send_message,
)
send_btn.place(x=350, y=485, width=90, height=40)

# تشغيل التطبيق
root.mainloop()
