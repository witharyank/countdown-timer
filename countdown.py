import sys
import tkinter as tk
from tkinter import ttk, messagebox


class CountdownTimer:

    def __init__(self, root):

        self.root = root
        self.root.title("Modern Countdown Timer")

        self.WIDTH = 560
        self.HEIGHT = 500

        x = (self.root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.HEIGHT // 2)

        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.root.resizable(False, False)

        self.bg = "#0F172A"
        self.card = "#111827"
        self.text = "#F8FAFC"
        self.primary = "#3B82F6"
        self.success = "#22C55E"
        self.warning = "#F59E0B"
        self.danger = "#EF4444"
        self.secondary = "#94A3B8"

        self.root.configure(bg=self.bg)

        self.running = False
        self.paused = False
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

            for _ in range(3):
                winsound.Beep(1200, 250)

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

            return total_seconds

        except Exception:

            messagebox.showerror(
                "Invalid Input",
                "Use formats:\n\nSS\nMM:SS\nHH:MM:SS"
            )

            return None

    # ---------------- TIMER ---------------- #

    def start_timer(self):

        if self.running:
            return

        if not self.paused:

            total = self.sanitize_time_input(self.entry.get())

            if total is None:
                return

            self.remaining_time = total
            self.total_time = total

        self.running = True
        self.paused = False

        self.entry.config(state="disabled")

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="normal")

        self.status_label.config(
            text="Running",
            fg=self.success
        )

        self.countdown()

    def pause_timer(self):

        if not self.running:
            return

        self.running = False
        self.paused = True

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")
        self.start_btn.config(state="disabled")

        self.status_label.config(
            text="Paused",
            fg=self.warning
        )

    def resume_timer(self):

        if not self.paused:
            return

        self.running = True
        self.paused = False

        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")

        self.status_label.config(
            text="Running",
            fg=self.success
        )

        self.countdown()

    def reset_timer(self):

        self.running = False
        self.paused = False

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.remaining_time = 0
        self.total_time = 0

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
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

        self.status_label.config(
            text="Ready",
            fg=self.secondary
        )

    # ---------------- COUNTDOWN ---------------- #

    def countdown(self):

        if not self.running:
            return

        if self.remaining_time > 0:

            h, rem = divmod(self.remaining_time, 3600)
            m, s = divmod(rem, 60)

            formatted = f"{h:02d}:{m:02d}:{s:02d}"

            self.timer_label.config(text=formatted)

            progress = (
                (self.total_time - self.remaining_time)
                / self.total_time
            ) * 100

            self.progress["value"] = progress

            if self.remaining_time <= 10:
                self.timer_label.config(fg=self.danger)
            else:
                self.timer_label.config(fg=self.success)

            self.remaining_time -= 1

            self.after_id = self.root.after(
                1000,
                self.countdown
            )

        else:

            self.running = False

            self.progress["value"] = 100

            self.flash_animation()

            self.play_sound()

            self.status_label.config(
                text="Completed",
                fg=self.primary
            )

            messagebox.showinfo(
                "Finished",
                "Time's up!"
            )

            self.reset_timer()

    # ---------------- FLASH EFFECT ---------------- #

    def flash_animation(self):

        self.flash_count = 0
        self.flash()

    def flash(self):

        if self.flash_count >= 6:
            self.timer_label.config(fg=self.success)
            return

        current = self.timer_label.cget("fg")

        new_color = (
            self.danger
            if current == self.success
            else self.success
        )

        self.timer_label.config(fg=new_color)

        self.flash_count += 1

        self.root.after(150, self.flash)

    # ---------------- PRESET TIMES ---------------- #

    def set_preset(self, value):

        self.entry.config(state="normal")

        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

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

    # ---------------- BUTTON EFFECTS ---------------- #

    def add_hover(self, button, color, hover):

        button.bind(
            "<Enter>",
            lambda e: button.config(bg=hover)
        )

        button.bind(
            "<Leave>",
            lambda e: button.config(bg=color)
        )

    # ---------------- STYLES ---------------- #

    def create_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "TProgressbar",
            thickness=14,
            troughcolor="#1E293B",
            background=self.primary,
            bordercolor="#1E293B",
            lightcolor=self.primary,
            darkcolor=self.primary
        )

    # ---------------- UI ---------------- #

    def create_ui(self):

        title = tk.Label(
            self.root,
            text="COUNTDOWN TIMER",
            font=("Helvetica", 26, "bold"),
            bg=self.bg,
            fg=self.text
        )

        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Modern Productivity Timer",
            font=("Helvetica", 11),
            bg=self.bg,
            fg=self.secondary
        )

        subtitle.pack()

        card = tk.Frame(
            self.root,
            bg=self.card
        )

        card.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )

        self.timer_label = tk.Label(
            card,
            text="00:00:00",
            font=("Consolas", 50, "bold"),
            bg=self.card,
            fg=self.success
        )

        self.timer_label.pack(pady=(35, 10))

        self.status_label = tk.Label(
            card,
            text="Ready",
            font=("Helvetica", 12, "bold"),
            bg=self.card,
            fg=self.secondary
        )

        self.status_label.pack()

        self.progress = ttk.Progressbar(
            card,
            mode="determinate",
            length=420
        )

        self.progress.pack(pady=25)

        self.entry = tk.Entry(
            card,
            font=("Helvetica", 18),
            width=15,
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

        preset_frame = tk.Frame(
            card,
            bg=self.card
        )

        preset_frame.pack(pady=10)

        presets = [
            ("1 Min", "00:01:00"),
            ("5 Min", "00:05:00"),
            ("10 Min", "00:10:00"),
            ("25 Min", "00:25:00")
        ]

        for text, value in presets:

            btn = tk.Button(
                preset_frame,
                text=text,
                bg="#1E293B",
                fg="white",
                relief="flat",
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda v=value: self.set_preset(v)
            )

            btn.pack(side="left", padx=5)

        button_frame = tk.Frame(
            card,
            bg=self.card
        )

        button_frame.pack(pady=25)

        self.start_btn = tk.Button(
            button_frame,
            text="Start",
            width=10,
            height=2,
            bg=self.primary,
            fg="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            command=self.start_timer
        )

        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = tk.Button(
            button_frame,
            text="Pause",
            width=10,
            height=2,
            bg=self.warning,
            fg="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.pause_timer
        )

        self.pause_btn.grid(row=0, column=1, padx=6)

        self.resume_btn = tk.Button(
            button_frame,
            text="Resume",
            width=10,
            height=2,
            bg=self.success,
            fg="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.resume_timer
        )

        self.resume_btn.grid(row=0, column=2, padx=6)

        self.reset_btn = tk.Button(
            button_frame,
            text="Reset",
            width=10,
            height=2,
            bg=self.danger,
            fg="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.reset_timer
        )

        self.reset_btn.grid(row=0, column=3, padx=6)

        self.add_hover(
            self.start_btn,
            self.primary,
            "#2563EB"
        )

        self.add_hover(
            self.pause_btn,
            self.warning,
            "#D97706"
        )

        self.add_hover(
            self.resume_btn,
            self.success,
            "#16A34A"
        )

        self.add_hover(
            self.reset_btn,
            self.danger,
            "#DC2626"
        )

        footer = tk.Label(
            self.root,
            text="Enter → Start | Space → Pause | R → Reset",
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