import tkinter as tk
from tkinter import messagebox

running = False
remaining_time = 0

def parse_time(time_str):
    try:
        parts = list(map(int, time_str.split(":")))
        while len(parts) < 3:
            parts.insert(0, 0)  # support MM:SS or SS input too
        h, m, s = parts
        return h * 3600 + m * 60 + s
    except:
        messagebox.showerror("Invalid Input", "Please enter time in HH:MM:SS format")
        return None

def start_timer():
    global running, remaining_time
    if not running:
        if remaining_time == 0:
            time_str = entry.get()
            total_seconds = parse_time(time_str)
            if total_seconds is None or total_seconds <= 0:
                return
            remaining_time = total_seconds
        running = True
        start_button.config(state="disabled")
        pause_button.config(state="normal")
        reset_button.config(state="normal")
        countdown()

def pause_timer():
    global running
    running = False
    start_button.config(state="normal")
    pause_button.config(state="disabled")

def reset_timer():
    global running, remaining_time
    running = False
    remaining_time = 0
    timer_label.config(text="00:00:00")
    start_button.config(state="normal")
    pause_button.config(state="disabled")
    reset_button.config(state="disabled")

def countdown():
    global remaining_time, running
    if running and remaining_time > 0:
        hrs, rem = divmod(remaining_time, 3600)
        mins, secs = divmod(rem, 60)
        timer_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
        remaining_time -= 1
        root.after(1000, countdown)
    elif remaining_time == 0 and running:
        running = False
        messagebox.showinfo("Time's Up!", "⏰ Countdown Complete!")
        reset_timer()

root = tk.Tk()
root.title("⏳ Countdown Timer")
root.geometry("360x280")
root.resizable(False, False)
root.config(bg="#1E1E2E")

title_label = tk.Label(root, text="Countdown Timer", font=("Helvetica", 18, "bold"),
                       bg="#1E1E2E", fg="#FFD700")
title_label.pack(pady=10)

timer_label = tk.Label(root, text="00:00:00", font=("Helvetica", 44, "bold"),
                       bg="#1E1E2E", fg="#00FFAA")
timer_label.pack(pady=10)

# === Input Field ===
entry = tk.Entry(root, font=("Helvetica", 14), width=12, justify="center")
entry.pack(pady=5)
entry.insert(0, "00:01:00")  # default 1 minute

# === Button Frame ===
button_frame = tk.Frame(root, bg="#1E1E2E")
button_frame.pack(pady=15)

start_button = tk.Button(button_frame, text="Start", font=("Helvetica", 12, "bold"),
                         bg="#00A2FF", fg="white", width=8, command=start_timer)
start_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(button_frame, text="Pause", font=("Helvetica", 12, "bold"),
                         bg="#FFB200", fg="white", width=8, command=pause_timer, state="disabled")
pause_button.grid(row=0, column=1, padx=5)

reset_button = tk.Button(button_frame, text="Reset", font=("Helvetica", 12, "bold"),
                         bg="#FF4B4B", fg="white", width=8, command=reset_timer, state="disabled")
reset_button.grid(row=0, column=2, padx=5)

footer_label = tk.Label(root, text="Enter time in HH:MM:SS format",
                        font=("Helvetica", 10), bg="#1E1E2E", fg="#AAAAAA")
footer_label.pack(side="bottom", pady=5)

root.mainloop()
