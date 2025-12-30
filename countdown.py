import tkinter as tk
from tkinter import messagebox
import winsound

running = False
remaining_time = 0


def sanitize_time_input(time_str):
    """
    Accepts:
    SS
    MM:SS
    HH:MM:SS

    Auto-fixes:
    - extra spaces
    - overflow seconds/minutes
    - missing fields
    """

    try:
        time_str = time_str.strip()

        if not time_str:
            raise ValueError("Empty input")

        parts = list(map(int, time_str.split(":")))

        if any(p < 0 for p in parts):
            raise ValueError("Negative values not allowed")

        # Normalize to HH:MM:SS
        while len(parts) < 3:
            parts.insert(0, 0)

        h, m, s = parts

        # Normalize overflow
        m += s // 60
        s = s % 60

        h += m // 60
        m = m % 60

        total_seconds = h * 3600 + m * 60 + s

        if total_seconds <= 0:
            raise ValueError("Time must be greater than zero")

        return total_seconds, f"{h:02d}:{m:02d}:{s:02d}"

    except Exception:
        messagebox.showerror(
            "Invalid Input",
            "Enter time as:\n"
            "SS\nMM:SS\nor HH:MM:SS\n\n"
            "Example:\n90 → 00:01:30"
        )
        return None, None


def start_timer():
    global running, remaining_time

    if not running:
        if remaining_time == 0:
            total_seconds, formatted = sanitize_time_input(entry.get())
            if total_seconds is None:
                return

            remaining_time = total_seconds
            entry.delete(0, tk.END)
            entry.insert(0, formatted)

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
        for _ in range(3):
            winsound.Beep(1200, 300)

        messagebox.showinfo("Time's Up!", "⏰ Countdown Complete!")
        reset_timer()


# ---------------- UI ---------------- #

root = tk.Tk()
root.title("⏳ Countdown Timer")
root.geometry("360x280")
root.resizable(False, False)
root.config(bg="#1E1E2E")

root.bind("<Return>", lambda e: start_timer())
root.bind("<space>", lambda e: pause_timer())
root.bind("r", lambda e: reset_timer())

title_label = tk.Label(
    root,
    text="Countdown Timer",
    font=("Helvetica", 18, "bold"),
    bg="#1E1E2E",
    fg="#FFD700"
)
title_label.pack(pady=10)

timer_label = tk.Label(
    root,
    text="00:00:00",
    font=("Helvetica", 44, "bold"),
    bg="#1E1E2E",
    fg="#00FFAA"
)
timer_label.pack(pady=10)

entry = tk.Entry(root, font=("Helvetica", 14), width=12, justify="center")
entry.pack(pady=5)
entry.insert(0, "00:01:00")

button_frame = tk.Frame(root, bg="#1E1E2E")
button_frame.pack(pady=15)

start_button = tk.Button(
    button_frame, text="Start", font=("Helvetica", 12, "bold"),
    bg="#00A2FF", fg="white", width=8, command=start_timer
)
start_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(
    button_frame, text="Pause", font=("Helvetica", 12, "bold"),
    bg="#FFB200", fg="white", width=8,
    command=pause_timer, state="disabled"
)
pause_button.grid(row=0, column=1, padx=5)

reset_button = tk.Button(
    button_frame, text="Reset", font=("Helvetica", 12, "bold"),
    bg="#FF4B4B", fg="white", width=8,
    command=reset_timer, state="disabled"
)
reset_button.grid(row=0, column=2, padx=5)

footer_label = tk.Label(
    root,
    text="Accepted formats: SS | MM:SS | HH:MM:SS",
    font=("Helvetica", 10),
    bg="#1E1E2E",
    fg="#AAAAAA"
)
footer_label.pack(side="bottom", pady=5)

root.mainloop()
