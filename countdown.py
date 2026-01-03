import sys
import tkinter as tk
from tkinter import messagebox



class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("⏳ Countdown Timer")
        self.root.geometry("360x300")
        self.root.resizable(False, False)
        self.root.config(bg="#1E1E2E")

        self.running = False
        self.remaining_time = 0

        self.create_ui()
        self.bind_keys()

    # ---------------- SOUND ---------------- #
    def play_sound(self):
        if sys.platform == "win32":
            import winsound
            winsound.Beep(1200, 300)
        else:
            self.root.bell()

    # ---------------- INPUT HANDLING ---------------- #
    def sanitize_time_input(self, time_str):
        try:
            time_str = time_str.strip()
            if not time_str:
                raise ValueError

            parts = list(map(int, time_str.split(":")))

            if any(p < 0 for p in parts):
                raise ValueError

            while len(parts) < 3:
                parts.insert(0, 0)

            h, m, s = parts

            m += s // 60
            s %= 60

            h += m // 60
            m %= 60

            total_seconds = h * 3600 + m * 60 + s

            if total_seconds <= 0:
                raise ValueError

            return total_seconds, f"{h:02d}:{m:02d}:{s:02d}"

        except Exception:
            messagebox.showerror(
                "Invalid Input",
                "Enter time as:\n"
                "SS\nMM:SS\nor HH:MM:SS\n\n"
                "Example:\n90 → 00:01:30"
            )
            return None, None

    # ---------------- TIMER CONTROLS ---------------- #
    def start_timer(self):
        if not self.running:
            if self.remaining_time == 0:
                total, formatted = self.sanitize_time_input(self.entry.get())
                if total is None:
                    return

                self.remaining_time = total
                self.entry.delete(0, tk.END)
                self.entry.insert(0, formatted)

            self.running = True
            self.entry.config(state="disabled")
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.reset_btn.config(state="normal")

            self.countdown()

    def pause_timer(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

    def reset_timer(self):
        self.running = False
        self.remaining_time = 0
        self.timer_label.config(text="00:00:00", fg="#00FFAA")

        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "00:01:00")
        self.entry.focus_set()

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

    # ---------------- COUNTDOWN ---------------- #
    def countdown(self):
        if self.running and self.remaining_time > 0:
            h, rem = divmod(self.remaining_time, 3600)
            m, s = divmod(rem, 60)

            self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            self.remaining_time -= 1

            self.root.after(1000, self.countdown)

        elif self.remaining_time == 0 and self.running:
            self.running = False
            self.flash_animation()

            for _ in range(3):
                self.play_sound()

            messagebox.showinfo("Time's Up!", "⏰ Countdown Complete!")
            self.reset_timer()

    # ---------------- VISUAL EFFECT ---------------- #
    def flash_animation(self):
        for _ in range(4):
            self.timer_label.config(fg="#FF4B4B")
            self.root.update()
            self.root.after(200)

            self.timer_label.config(fg="#00FFAA")
            self.root.update()
            self.root.after(200)

    # ---------------- KEYBOARD SHORTCUTS ---------------- #
    def bind_keys(self):
        self.root.bind("<Return>", lambda e: self.start_timer())
        self.root.bind("<space>", lambda e: self.pause_timer())
        self.root.bind("r", lambda e: self.reset_timer())

    # ---------------- UI ---------------- #
    def create_ui(self):
        title = tk.Label(
            self.root,
            text="Countdown Timer",
            font=("Helvetica", 18, "bold"),
            bg="#1E1E2E",
            fg="#FFD700"
        )
        title.pack(pady=10)

        self.timer_label = tk.Label(
            self.root,
            text="00:00:00",
            font=("Helvetica", 44, "bold"),
            bg="#1E1E2E",
            fg="#00FFAA"
        )
        self.timer_label.pack(pady=10)

        self.entry = tk.Entry(
            self.root,
            font=("Helvetica", 14),
            width=12,
            justify="center"
        )
        self.entry.pack(pady=5)
        self.entry.insert(0, "00:01:00")

        btn_frame = tk.Frame(self.root, bg="#1E1E2E")
        btn_frame.pack(pady=15)

        self.start_btn = tk.Button(
            btn_frame, text="Start", width=8,
            font=("Helvetica", 12, "bold"),
            bg="#00A2FF", fg="white",
            command=self.start_timer
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            btn_frame, text="Pause", width=8,
            font=("Helvetica", 12, "bold"),
            bg="#FFB200", fg="white",
            command=self.pause_timer,
            state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(
            btn_frame, text="Reset", width=8,
            font=("Helvetica", 12, "bold"),
            bg="#FF4B4B", fg="white",
            command=self.reset_timer,
            state="disabled"
        )
        self.reset_btn.grid(row=0, column=2, padx=5)

        footer = tk.Label(
            self.root,
            text="Formats: SS | MM:SS | HH:MM:SS   |   Enter → Start   Space → Pause   R → Reset",
            font=("Helvetica", 9),
            bg="#1E1E2E",
            fg="#AAAAAA"
        )
        footer.pack(side="bottom", pady=6)


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()
