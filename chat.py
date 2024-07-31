import os
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from groq import Groq
from datetime import datetime

os.environ['GROQ_API_KEY'] = 'API_KEY'

client = Groq()

root = tk.Tk()
root.title("股票助理(LLAMA 3.1-70B)")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="white")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(frame,bg="#F0FFF0",width=480,height=450)
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas,bg="#F0FFF0",width=480)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def on_mouse_wheel(event):
    if canvas.yview() != (0.0, 1.0):
        canvas.yview_scroll(int(-1*(event.delta/100)), "units")

canvas.bind_all("<MouseWheel>", on_mouse_wheel)

entry_frame = tk.Frame(root, bg="white",height=60)
entry_frame.pack(fill=tk.X, pady=5)

entry = tk.Entry(entry_frame, width=10)
entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
date_shown = False
def round_rectangle(canvas, x1, y1, x2, y2, radius=100, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)
def add_message(text, sender):
    global date_shown
    now = datetime.now()
    current_time = now.strftime('%p %I:%M')
    if 'AM' in current_time:
        current_time = current_time.replace('AM', '早上')
    else:
        current_time = current_time.replace('PM', '下午')

    if not date_shown:
        current_date = now.strftime('%Y年%m月%d日')
        date_canvas = tk.Canvas(scrollable_frame, width=480, height=45, bg=scrollable_frame.cget("bg"), highlightthickness=0)
        round_rectangle(date_canvas, 160, 0, 320, 30, radius=15, fill="#D9D9D9", outline="")
        date_canvas.create_text(240, 15, text=current_date, fill="#000000", font=("Arial", 10, "bold"))
        date_canvas.pack(pady=5)
        date_shown = True

    container_frame = tk.Frame(scrollable_frame, bg=scrollable_frame.cget("bg"))
    container_frame.pack(anchor="w" if sender == "ai" else "e", padx=5)

    sender_label = tk.Label(container_frame, text="用戶" if sender == "user" else "AI", bg=scrollable_frame.cget("bg"), font=("Arial", 8, "bold"))
    sender_label.pack(anchor="e" if sender == "user" else "w", padx=5, pady=5)

    message_frame = tk.Frame(container_frame, bg="#AFEEEE" if sender == "user" else "#FFE4B5", bd=5)
    message_frame.pack(anchor="e" if sender == "user" else "w")

    message_text = f"{text}"
    message_label = tk.Label(message_frame, text=message_text, bg="#AFEEEE" if sender == "user" else "#FFE4B5", wraplength=250, justify='left')
    message_label.pack(side="left" if sender == "user" else "right")

    timestamp_label = tk.Label(container_frame, text=current_time, bg=scrollable_frame.cget("bg"))
    timestamp_label.pack(side="right" if sender == "user" else "left", padx=5)

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

# def add_message(text, sender):
#     bubble_frame = tk.Frame(scrollable_frame, bg="lightblue" if sender == "user" else "lightgreen", bd=5)
#     bubble_frame.pack(anchor="e" if sender == "user" else "w", padx=10, pady=5)

#     message = tk.Label(bubble_frame, text=text, bg="lightblue" if sender == "user" else "lightgreen", wraplength=250, justify='left')
#     message.pack(side="right" if sender == "user" else "left")

#     canvas.update_idletasks()
#     canvas.yview_moveto(1.0)

def get_response():
    question = entry.get()
    if not question:
        return

    add_message(f"{question}", "user")

    entry.delete(0, tk.END)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a stock assistant, can only answer stock-related questions, other questions can only be replied with \"我只能回答與股票相關的問題。\"."},
            {"role": "user", "content": f"{question}，使用繁體中文回答"},
        ],
        model="llama-3.1-70b-versatile",
        temperature=0.5,
        max_tokens=800,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    response = chat_completion.choices[0].message.content
    add_message(f"{response}", "ai")

entry.bind("<Return>", lambda event: get_response())


submit_img = tk.PhotoImage(file=r"C:\project\llama3.1\send_20.png")

button = tk.Button(entry_frame, image=submit_img, command=get_response, borderwidth=0,width=50,height=20,bg="#FFFFFF")
button.pack(side=tk.RIGHT)

add_message("我是你的股票助理，負責解答您所有與股票相關的問題", "ai")

entry.focus_set()
root.mainloop()
