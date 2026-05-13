import sys
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class CountdownTimer:

    def __init__(self, root):

        self.root = root
        self.root.title("Advanced Countdown Timer")

        self.WIDTH = 500
        self.HEIGHT = 420

        x = (self.root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.HEIGHT // 2)

        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.root.resizable(False, False)

        self.bg = "#0F172A"
        self.card = "#111827"
        self.text = "#F8FAFC"
        self.primary = "#3B82F6"
        self.success = "#10B981"
        self.warning = "#F59E0B"
        self.danger = "#EF4444"
        self.secondary = "#94A3B8"

        self.root.configure(bg=self.bg)

        self.running = False
        self.remaining_time = 0
        self.total_time = 0
        self.after_id = None

        self.create_styles()
        self.create_ui()
        self.bind_keys()

    # ---------------- SOUND ---------------- #

    def play_sound(self):

        if sys.platform == "win32":

            import winsound

            for _ in range(2):
                winsound.Beep(1200, 250)

        else:
            self.root.bell()

    # ---------------- TIME FORMAT ---------------- #

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

            formatted = f"{h:02d}:{m:02d}:{s:02d}"

            return total_seconds, formatted

        except Exception:

            messagebox.showerror(
                "Invalid Input",
                "Enter time in formats:\n\n"
                "SS\nMM:SS\nHH:MM:SS\n\n"
                "Examples:\n90\n05:30\n01:15:45"
            )

            return None, None

    # ---------------- TIMER LOGIC ---------------- #

    def start_timer(self):

        if self.running:
            return

        if self.remaining_time == 0:

            total, formatted = self.sanitize_time_input(
                self.entry.get()
            )

            if total is None:
                return

            self.remaining_time = total
            self.total_time = total

            self.entry.delete(0, tk.END)
            self.entry.insert(0, formatted)

        self.running = True

        self.entry.config(state="disabled")

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.reset_btn.config(state="normal")

        self.status_label.config(
            text="Running",
            foreground=self.success
        )

        self.countdown()

    def pause_timer(self):

        self.running = False

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

        self.status_label.config(
            text="Paused",
            foreground=self.warning
        )

    def reset_timer(self):

        self.running = False
        self.remaining_time = 0
        self.total_time = 0

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.timer_label.config(
            text="00:00:00",
            fg=self.success
        )

        self.progress["value"] = 0

        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "00:01:00")

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

        self.status_label.config(
            text="Ready",
            foreground=self.secondary
        )

    # ---------------- COUNTDOWN ---------------- #

    def countdown(self):

        if self.running and self.remaining_time > 0:

            h, rem = divmod(self.remaining_time, 3600)
            m, s = divmod(rem, 60)

            formatted = f"{h:02d}:{m:02d}:{s:02d}"

            self.timer_label.config(text=formatted)

            progress_value = (
                (self.total_time - self.remaining_time)
                / self.total_time
            ) * 100

            self.progress["value"] = progress_value

            if self.remaining_time <= 10:
                self.timer_label.config(fg=self.danger)
            else:
                self.timer_label.config(fg=self.success)

            self.remaining_time -= 1

            self.after_id = self.root.after(
                1000,
                self.countdown
            )

        elif self.remaining_time == 0 and self.running:

            self.running = False

            self.progress["value"] = 100

            self.flash_animation()

            self.play_sound()

            self.status_label.config(
                text="Completed",
                foreground=self.primary
            )

            messagebox.showinfo(
                "Timer Finished",
                "Countdown completed successfully!"
            )

            self.reset_timer()

    # ---------------- FLASH EFFECT ---------------- #

    def flash_animation(self):

        for _ in range(6):

            self.timer_label.config(fg=self.danger)

            self.root.update()

            time.sleep(0.15)

            self.timer_label.config(fg=self.success)

            self.root.update()

            time.sleep(0.15)

    # ---------------- SHORTCUTS ---------------- #

    def bind_keys(self):

        self.root.bind(
            "<Return>",
            lambda e: self.start_timer()
        )

        self.root.bind(
            "<space>",
            lambda e: self.pause_timer()
        )

        self.root.bind(
            "r",
            lambda e: self.reset_timer()
        )

    # ---------------- STYLES ---------------- #

    def create_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "TProgressbar",
            thickness=12,
            troughcolor="#1E293B",
            background=self.primary,
            bordercolor="#1E293B",
            lightcolor=self.primary,
            darkcolor=self.primary
        )

    # ---------------- UI ---------------- #

    def create_ui(self):

        top_frame = tk.Frame(
            self.root,
            bg=self.bg
        )

        top_frame.pack(
            fill="x",
            pady=20
        )

        title = tk.Label(
            top_frame,
            text="COUNTDOWN TIMER",
            font=("Helvetica", 24, "bold"),
            bg=self.bg,
            fg=self.text
        )

        title.pack()

        subtitle = tk.Label(
            top_frame,
            text="Modern Productivity Timer",
            font=("Helvetica", 11),
            bg=self.bg,
            fg=self.secondary
        )

        subtitle.pack(pady=4)

        card = tk.Frame(
            self.root,
            bg=self.card,
            bd=0
        )

        card.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

        self.timer_label = tk.Label(
            card,
            text="00:00:00",
            font=("Consolas", 46, "bold"),
            bg=self.card,
            fg=self.success
        )

        self.timer_label.pack(pady=(35, 10))

        self.status_label = tk.Label(
            card,
            text="Ready",
            font=("Helvetica", 11, "bold"),
            bg=self.card,
            fg=self.secondary
        )

        self.status_label.pack()

        self.progress = ttk.Progressbar(
            card,
            mode="determinate",
            length=380
        )

        self.progress.pack(pady=25)

        self.entry = tk.Entry(
            card,
            font=("Helvetica", 16),
            width=14,
            justify="center",
            relief="flat",
            bg="#1E293B",
            fg="white",
            insertbackground="white"
        )

        self.entry.pack(ipady=10)

        self.entry.insert(0, "00:01:00")

        hint = tk.Label(
            card,
            text="Formats: SS | MM:SS | HH:MM:SS",
            font=("Helvetica", 10),
            bg=self.card,
            fg=self.secondary
        )

        hint.pack(pady=10)

        button_frame = tk.Frame(
            card,
            bg=self.card
        )

        button_frame.pack(pady=20)

        self.start_btn = tk.Button(
            button_frame,
            text="Start",
            width=10,
            height=2,
            bg=self.primary,
            fg="white",
            activebackground=self.primary,
            activeforeground="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            command=self.start_timer
        )

        self.start_btn.grid(
            row=0,
            column=0,
            padx=8
        )

        self.pause_btn = tk.Button(
            button_frame,
            text="Pause",
            width=10,
            height=2,
            bg=self.warning,
            fg="white",
            activebackground=self.warning,
            activeforeground="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.pause_timer
        )

        self.pause_btn.grid(
            row=0,
            column=1,
            padx=8
        )

        self.reset_btn = tk.Button(
            button_frame,
            text="Reset",
            width=10,
            height=2,
            bg=self.danger,
            fg="white",
            activebackground=self.danger,
            activeforeground="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.reset_timer
        )

        self.reset_btn.grid(
            row=0,
            column=2,
            padx=8
        )

        footer = tk.Label(
            self.root,
            text="Enter → Start    Space → Pause    R → Reset",
            font=("Helvetica", 10),
            bg=self.bg,
            fg=self.secondary
        )

        footer.pack(
            side="bottom",
            pady=12
        )


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    root = tk.Tk()

    app = CountdownTimer(root)

    root.mainloop()