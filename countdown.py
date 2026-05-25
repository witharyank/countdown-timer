import sys
import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
import json
import os

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Productivity Suite")

        # Window Dimension
        self.WIDTH = 580
        self.HEIGHT = 650
        
        # Center Window on Screen
        x = (self.root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.HEIGHT // 2)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.root.resizable(False, False)

        # ---------------- DESIGN SYSTEMS & THEMES ---------------- #
        self.THEMES = {
            "Slate Dark": {
                "bg": "#0F172A",
                "card": "#1E293B",
                "text": "#F8FAFC",
                "primary": "#3B82F6",
                "success": "#10B981",
                "warning": "#F59E0B",
                "danger": "#EF4444",
                "secondary": "#94A3B8",
                "track": "#334155",
                "button_bg": "#334155",
                "button_fg": "#F8FAFC",
                "entry_bg": "#334155"
            },
            "Cyberpunk": {
                "bg": "#0B0314",
                "card": "#1A092A",
                "text": "#00FFFF",
                "primary": "#FF007F",
                "success": "#00FF66",
                "warning": "#FFCC00",
                "danger": "#FF3333",
                "secondary": "#BA9BC9",
                "track": "#3D185A",
                "button_bg": "#3D185A",
                "button_fg": "#00FFFF",
                "entry_bg": "#3D185A"
            },
            "Forest": {
                "bg": "#091412",
                "card": "#112C26",
                "text": "#E8F5E9",
                "primary": "#81C784",
                "success": "#4CAF50",
                "warning": "#FFB74D",
                "danger": "#E57373",
                "secondary": "#A5D6A7",
                "track": "#1A443A",
                "button_bg": "#1A443A",
                "button_fg": "#E8F5E9",
                "entry_bg": "#1A443A"
            },
            "Sunset": {
                "bg": "#180914",
                "card": "#2C1224",
                "text": "#FCE7F3",
                "primary": "#F43F5E",
                "success": "#34D399",
                "warning": "#FBBF24",
                "danger": "#EF4444",
                "secondary": "#F472B6",
                "track": "#4E1E3F",
                "button_bg": "#4E1E3F",
                "button_fg": "#FCE7F3",
                "entry_bg": "#4E1E3F"
            },
            "Crisp Light": {
                "bg": "#F8FAFC",
                "card": "#FFFFFF",
                "text": "#0F172A",
                "primary": "#2563EB",
                "success": "#16A34A",
                "warning": "#D97706",
                "danger": "#DC2626",
                "secondary": "#64748B",
                "track": "#E2E8F0",
                "button_bg": "#F1F5F9",
                "button_fg": "#0F172A",
                "entry_bg": "#F1F5F9"
            }
        }

        # ---------------- CONFIG AND PERSISTENCE ---------------- #
        self.CONFIG_FILE = ".timer_config.json"
        self.current_theme = "Slate Dark"
        self.presets = [
            ("1 Min", "00:01:00"),
            ("5 Min", "00:05:00"),
            ("10 Min", "00:10:00"),
            ("25 Min", "00:25:00")
        ]
        self.tick_sound_enabled = tk.BooleanVar(value=False)
        self.alert_style = tk.StringVar(value="Standard")

        self.load_config()

        # ---------------- STATE variables ---------------- #
        self.running = False
        self.paused = False
        self.remaining_time = 0.0 # Float for high precision
        self.total_time = 0.0
        self.target_time = 0.0 # system monotonic timestamp for end
        self.after_id = None
        
        # Pomodoro Mode variables
        self.pomodoro_mode = False
        self.pomodoro_state = "none" # "work", "short_break", "long_break", "none"
        self.pomodoro_rounds = 0 # Out of 4

        # Initialize UI Components
        self.create_styles()
        self.create_ui()
        self.bind_keys()
        self.apply_theme()
        
        # Set default values based on current mode
        self.toggle_mode(to_pomodoro=False)

    # ---------------- PERSISTENCE ENGINE ---------------- #
    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    if "theme" in data and data["theme"] in self.THEMES:
                        self.current_theme = data["theme"]
                    if "presets" in data:
                        # Validate format of presets
                        self.presets = [(item[0], item[1]) for item in data["presets"]]
                    if "tick_sound" in data:
                        self.tick_sound_enabled.set(data["tick_sound"])
                    if "alert_style" in data:
                        self.alert_style.set(data["alert_style"])
            except Exception:
                pass # Fallback to default if error loading

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump({
                    "theme": self.current_theme,
                    "presets": self.presets,
                    "tick_sound": self.tick_sound_enabled.get(),
                    "alert_style": self.alert_style.get()
                }, f, indent=4)
        except Exception:
            pass

    # ---------------- AUDIO & COMPONENT METRICS ---------------- #
    def play_sound(self):
        style = self.alert_style.get()
        if style == "Silent":
            return
            
        if sys.platform == "win32":
            import winsound
            if style == "Standard":
                for _ in range(3):
                    if not self.root: break
                    winsound.Beep(1200, 250)
            elif style == "Chime":
                for freq in [800, 1000, 1200]:
                    if not self.root: break
                    winsound.Beep(freq, 200)
            elif style == "Siren":
                for _ in range(2):
                    if not self.root: break
                    winsound.Beep(1500, 150)
                    winsound.Beep(1200, 150)
        else:
            # Non-windows fallbacks
            for _ in range(3):
                self.root.bell()
                time.sleep(0.3)

    def play_tick(self):
        if sys.platform == "win32":
            import winsound
            try:
                winsound.Beep(2000, 10) # Elegant mechanical click sound
            except Exception:
                pass

    # ---------------- HIGH PRECISION TIMING ENGINE ---------------- #
    def start_timer(self):
        if self.running:
            return

        if not self.paused:
            if self.pomodoro_mode:
                # Set initial pomodoro values
                if self.pomodoro_state == "none":
                    self.pomodoro_state = "work"
                    self.pomodoro_rounds = 0
                
                # Fetch default durations
                if self.pomodoro_state == "work":
                    total = 25 * 60
                elif self.pomodoro_state == "short_break":
                    total = 5 * 60
                else: # long break
                    total = 15 * 60
            else:
                total = self.sanitize_time_input(self.entry.get())
                if total is None:
                    return

            self.remaining_time = float(total)
            self.total_time = float(total)

        self.running = True
        self.paused = False
        self.target_time = time.monotonic() + self.remaining_time

        # Update Form controls
        self.entry.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="normal")
        self.theme_dropdown.config(state="disabled")
        self.mode_timer_btn.config(state="disabled")
        self.mode_pomo_btn.config(state="disabled")

        theme = self.THEMES[self.current_theme]
        status_color = theme["success"] if self.pomodoro_state in ["work", "none"] else theme["warning"]
        self.status_label.config(
            text=self.get_status_text(),
            fg=status_color
        )

        self.countdown()

    def pause_timer(self):
        if not self.running:
            return

        self.running = False
        self.paused = True
        
        # Calculate exactly how much time is left before cancelling
        self.remaining_time = max(0.0, self.target_time - time.monotonic())

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")
        self.start_btn.config(state="disabled")

        theme = self.THEMES[self.current_theme]
        self.status_label.config(
            text="Paused",
            fg=theme["warning"]
        )

    def resume_timer(self):
        if not self.paused:
            return

        self.running = True
        self.paused = False
        
        # Re-calibrate target time base on remaining fractional seconds
        self.target_time = time.monotonic() + self.remaining_time

        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")

        theme = self.THEMES[self.current_theme]
        status_color = theme["success"] if self.pomodoro_state in ["work", "none"] else theme["warning"]
        self.status_label.config(
            text=self.get_status_text(),
            fg=status_color
        )

        self.countdown()

    def reset_timer(self):
        self.running = False
        self.paused = False

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.remaining_time = 0.0
        self.total_time = 0.0
        
        # Unlock Form Elements
        self.entry.config(state="normal")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")
        self.theme_dropdown.config(state="readonly")
        self.mode_timer_btn.config(state="normal")
        self.mode_pomo_btn.config(state="normal")

        if self.pomodoro_mode:
            self.pomodoro_state = "none"
            self.pomodoro_rounds = 0
            self.remaining_time = 25 * 60
            self.total_time = 25 * 60
            self.update_pomodoro_ui()
        else:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "00:01:00")

        self.draw_progress()

        theme = self.THEMES[self.current_theme]
        self.status_label.config(
            text="Ready",
            fg=theme["secondary"]
        )

    def countdown(self):
        if not self.running:
            return

        now = time.monotonic()
        remaining = self.target_time - now

        if remaining <= 0.0:
            self.remaining_time = 0.0
            self.running = False
            self.draw_progress()
            
            # Finished Trigger!
            self.flash_animation()
            self.play_sound()

            if self.pomodoro_mode:
                self.handle_pomodoro_completion()
            else:
                theme = self.THEMES[self.current_theme]
                self.status_label.config(
                    text="Completed",
                    fg=theme["primary"]
                )
                messagebox.showinfo("Time's up!", "The countdown has finished!")
                self.reset_timer()
        else:
            self.remaining_time = remaining
            self.draw_progress()
            
            # Sub-second high precision mechanical tick-tock sounds
            current_sec = math.ceil(remaining)
            if not hasattr(self, "last_sec") or self.last_sec != current_sec:
                self.last_sec = current_sec
                if self.tick_sound_enabled.get():
                    self.play_tick()

            # Poll frequently at 100ms for smooth sub-second updates
            self.after_id = self.root.after(100, self.countdown)

    def get_status_text(self):
        if not self.pomodoro_mode:
            return "Running"
        if self.pomodoro_state == "work":
            return f"Focusing (Round {self.pomodoro_rounds + 1}/4)"
        if self.pomodoro_state == "short_break":
            return "Short Break"
        if self.pomodoro_state == "long_break":
            return "Long Break"
        return "Ready"

    # ---------------- POMODORO STATE MACHINE ---------------- #
    def handle_pomodoro_completion(self):
        theme = self.THEMES[self.current_theme]
        if self.pomodoro_state == "work":
            self.pomodoro_rounds += 1
            if self.pomodoro_rounds < 4:
                self.pomodoro_state = "short_break"
                self.remaining_time = 5.0 * 60
                self.total_time = 5.0 * 60
                state_text = "Short Break"
                msg = "Focus Session complete! Time for a 5-minute break."
            else:
                self.pomodoro_state = "long_break"
                self.remaining_time = 15.0 * 60
                self.total_time = 15.0 * 60
                state_text = "Long Break"
                msg = "Fantastic! 4 focus sessions completed. Take a long 15-minute break!"
                self.pomodoro_rounds = 0 # reset cycle
            self.status_label.config(text=state_text, fg=theme["warning"])
        else:
            # Switch back to Focus Session
            self.pomodoro_state = "work"
            self.remaining_time = 25.0 * 60
            self.total_time = 25.0 * 60
            state_text = "Focus Session"
            msg = "Break is over! Time to get back to work."
            self.status_label.config(text=state_text, fg=theme["success"])

        self.running = False
        self.paused = False
        self.draw_progress()
        self.update_pomodoro_ui()

        # Unlock controls for the next phase
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="normal")
        self.theme_dropdown.config(state="readonly")
        self.mode_timer_btn.config(state="normal")
        self.mode_pomo_btn.config(state="normal")

        messagebox.showinfo("Pomodoro Update", msg)

    def update_pomodoro_ui(self):
        self.draw_pomodoro_dots()
        theme = self.THEMES[self.current_theme]
        if self.pomodoro_state == "work":
            self.pomodoro_indicator_label.config(text=f"Round {self.pomodoro_rounds + 1} of 4: Deep Work Session", fg=theme["success"])
        elif self.pomodoro_state == "short_break":
            self.pomodoro_indicator_label.config(text="Short Break: Rest & Recharge", fg=theme["warning"])
        elif self.pomodoro_state == "long_break":
            self.pomodoro_indicator_label.config(text="Long Break: Relax & Reflect", fg=theme["warning"])
        else:
            self.pomodoro_indicator_label.config(text="Pomodoro Cycles: 4 Focus Rounds", fg=theme["secondary"])

    # ---------------- VISUAL PROGRESS RING ---------------- #
    def draw_progress(self):
        theme = self.THEMES[self.current_theme]
        
        # Dimensions
        w, h = 220, 220
        cx, cy = w // 2, h // 2
        r = 90

        # Background track
        self.progress_canvas.itemconfig(self.canvas_track, outline=theme["track"])

        # Foreground Active Progress Arc
        if self.total_time > 0 and self.remaining_time > 0:
            percent = self.remaining_time / self.total_time
            extent = -percent * 360.0
            
            # Transition to danger color when < 10 seconds remain
            arc_color = theme["danger"] if self.remaining_time <= 10 else theme["primary"]
            self.progress_canvas.itemconfig(
                self.canvas_arc,
                extent=extent,
                outline=arc_color,
                state="normal"
            )
        else:
            extent = 0.0 if self.total_time == 0 else -360.0
            arc_color = theme["primary"]
            self.progress_canvas.itemconfig(
                self.canvas_arc,
                extent=extent,
                outline=arc_color
            )

        # Center Text Formatting
        total_seconds = math.ceil(self.remaining_time)
        h_val, rem = divmod(total_seconds, 3600)
        m_val, s_val = divmod(rem, 60)
        formatted = f"{h_val:02d}:{m_val:02d}:{s_val:02d}"

        # Color changes state-wise
        text_color = theme["text"]
        if self.running and self.remaining_time <= 10:
            text_color = theme["danger"]
        elif self.running:
            text_color = theme["success"]
        elif self.paused:
            text_color = theme["warning"]

        self.progress_canvas.itemconfig(
            self.canvas_text,
            text=formatted,
            fill=text_color
        )

    def draw_pomodoro_dots(self):
        self.pomo_dots_canvas.delete("all")
        if not self.pomodoro_mode:
            return

        theme = self.THEMES[self.current_theme]
        w, h = 180, 25
        cx = w // 2
        cy = h // 2

        # 4 circular rounds indicators
        dot_radius = 6
        spacing = 22
        start_x = cx - (3 * spacing) // 2

        for i in range(4):
            x = start_x + i * spacing
            fill_color = theme["success"] if i < self.pomodoro_rounds else theme["track"]
            self.pomo_dots_canvas.create_oval(
                x - dot_radius, cy - dot_radius,
                x + dot_radius, cy + dot_radius,
                fill=fill_color,
                outline=""
            )

    # ---------------- MODE CONTROLS ---------------- #
    def toggle_mode(self, to_pomodoro):
        if self.running:
            return

        self.pomodoro_mode = to_pomodoro
        theme = self.THEMES[self.current_theme]

        # Apply Segmented visual button toggle
        if self.pomodoro_mode:
            self.mode_timer_btn.config(bg=theme["button_bg"], fg=theme["secondary"])
            self.mode_pomo_btn.config(bg=theme["primary"], fg=theme["bg"])
            
            # UI adjustments
            self.timer_entry_label.pack_forget()
            self.entry.pack_forget()
            self.preset_tip_label.pack_forget()
            self.preset_frame.pack_forget()

            # Show Pomodoro components
            self.pomodoro_indicator_label.pack(pady=(10, 2))
            self.pomo_dots_canvas.pack(pady=2)

            self.pomodoro_state = "none"
            self.pomodoro_rounds = 0
            self.remaining_time = 25 * 60
            self.total_time = 25 * 60
            self.update_pomodoro_ui()
        else:
            self.mode_timer_btn.config(bg=theme["primary"], fg=theme["bg"])
            self.mode_pomo_btn.config(bg=theme["button_bg"], fg=theme["secondary"])

            # Hide Pomodoro components
            self.pomodoro_indicator_label.pack_forget()
            self.pomo_dots_canvas.pack_forget()

            # Show Timer inputs
            self.timer_entry_label.pack(pady=(10, 0))
            self.entry.pack(ipady=10, pady=5)
            self.preset_tip_label.pack(pady=(5, 5))
            self.preset_frame.pack(pady=5)

            self.remaining_time = 60
            self.total_time = 60
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "00:01:00")

        self.draw_progress()

    # ---------------- CUSTOM PRESETS & SANITIZATION ---------------- #
    def set_preset(self, value):
        if self.running:
            return
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        
        total = self.sanitize_time_input(value)
        if total:
            self.remaining_time = float(total)
            self.total_time = float(total)
            self.draw_progress()

    def add_custom_preset(self):
        val = self.entry.get().strip()
        total = self.sanitize_time_input(val)
        if total is None:
            return

        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        formatted = f"{h:02d}:{m:02d}:{s:02d}"

        # Clean button text name
        if h > 0:
            name = f"{h}h {m}m" if m > 0 else f"{h}h"
        elif m > 0:
            name = f"{m} Min"
        else:
            name = f"{s} Sec"

        # Check redundancy
        if any(item[1] == formatted for item in self.presets):
            messagebox.showinfo("Preset Info", "Preset already exists!")
            return

        if len(self.presets) >= 8:
            messagebox.showwarning("Limit Reached", "Max 8 presets allowed. Right-click a preset to delete.")
            return

        self.presets.append((name, formatted))
        self.save_config()
        self.render_preset_buttons()

    def delete_preset(self, value):
        if self.running:
            return
        
        # Filter out clicked value
        initial_len = len(self.presets)
        self.presets = [item for item in self.presets if item[1] != value]
        
        if len(self.presets) < initial_len:
            self.save_config()
            self.render_preset_buttons()
            messagebox.showinfo("Preset Deleted", "Preset has been removed!")

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
                "Invalid Format",
                "Please enter a valid format:\n\n- SS (e.g. 90)\n- MM:SS (e.g. 05:00)\n- HH:MM:SS (e.g. 01:30:00)"
            )
            return None

    # ---------------- VISUAL EFFECTS & HOVER ---------------- #
    def flash_animation(self):
        self.flash_count = 0
        self.flash()

    def flash(self):
        if self.flash_count >= 8:
            self.draw_progress()
            return

        theme = self.THEMES[self.current_theme]
        current_fill = self.progress_canvas.itemcget(self.canvas_text, "fill")
        
        # Toggle between Success and Danger
        new_color = theme["danger"] if current_fill == theme["success"] else theme["success"]
        self.progress_canvas.itemconfig(self.canvas_text, fill=new_color)
        
        self.flash_count += 1
        self.root.after(120, self.flash)

    def add_hover(self, button, normal_color, hover_color):
        button.bind("<Enter>", lambda e: button.config(bg=hover_color) if button["state"] != "disabled" else None)
        button.bind("<Leave>", lambda e: button.config(bg=normal_color) if button["state"] != "disabled" else None)

    # ---------------- SHORTCUT EVENT INTERFERENCE BLOCKS ---------------- #
    def bind_keys(self):
        self.root.bind("<Return>", self.handle_return_key)
        self.root.bind("<space>", self.handle_space_key)
        self.root.bind("r", self.handle_r_key)
        self.root.bind("R", self.handle_r_key)

    def handle_return_key(self, event):
        self.start_timer()

    def handle_space_key(self, event):
        # Stop short-cut trigger when typing in inputs
        if self.root.focus_get() == self.entry:
            return
        if self.running:
            self.pause_timer()
        elif self.paused:
            self.resume_timer()
        else:
            self.start_timer()
        return "break" # blocks standard scroll/button activation behavior

    def handle_r_key(self, event):
        if self.root.focus_get() == self.entry:
            return
        self.reset_timer()
        return "break"

    # ---------------- THEME & WIDGET ENGINES ---------------- #
    def apply_theme(self):
        theme = self.THEMES[self.current_theme]
        self.save_config()

        # Update root and title styling
        self.root.configure(bg=theme["bg"])
        self.title_label.config(bg=theme["bg"], fg=theme["text"])
        self.subtitle_label.config(bg=theme["bg"], fg=theme["secondary"])

        # Top panel
        self.top_panel.config(bg=theme["bg"])
        self.theme_label.config(bg=theme["bg"], fg=theme["text"])

        # Segmented controls
        self.mode_timer_btn.config(
            bg=theme["primary"] if not self.pomodoro_mode else theme["button_bg"],
            fg=theme["bg"] if not self.pomodoro_mode else theme["secondary"],
            activebackground=theme["primary"]
        )
        self.mode_pomo_btn.config(
            bg=theme["primary"] if self.pomodoro_mode else theme["button_bg"],
            fg=theme["bg"] if self.pomodoro_mode else theme["secondary"],
            activebackground=theme["primary"]
        )

        # Main frame/card container
        self.card.config(bg=theme["card"])
        self.progress_canvas.config(bg=theme["card"])

        # Sound & Settings Frame
        self.settings_card.config(bg=theme["card"])
        self.tick_checkbox.config(bg=theme["card"], fg=theme["text"], selectcolor=theme["bg"], activebackground=theme["card"], activeforeground=theme["text"])
        self.alert_label.config(bg=theme["card"], fg=theme["text"])

        # Pomodoro UI
        self.pomodoro_indicator_label.config(bg=theme["card"])
        self.pomo_dots_canvas.config(bg=theme["card"])
        self.update_pomodoro_ui()

        # Inputs Card elements
        self.timer_entry_label.config(bg=theme["card"], fg=theme["text"])
        self.entry.config(bg=theme["entry_bg"], fg=theme["text"], insertbackground=theme["text"])
        self.preset_tip_label.config(bg=theme["card"], fg=theme["secondary"])
        self.preset_frame.config(bg=theme["card"])
        self.render_preset_buttons()

        # Status Label
        self.status_label.config(bg=theme["card"])
        if not self.running and not self.paused:
            self.status_label.config(fg=theme["secondary"])
        elif self.paused:
            self.status_label.config(fg=theme["warning"])
        else:
            status_color = theme["success"] if self.pomodoro_state in ["work", "none"] else theme["warning"]
            self.status_label.config(fg=status_color)

        # Dynamic Button frame colors
        self.button_frame.config(bg=theme["card"])
        
        self.start_btn.config(bg=theme["primary"], fg=theme["bg"] if theme["bg"] != "#FFFFFF" else "white")
        self.pause_btn.config(bg=theme["warning"], fg="white")
        self.resume_btn.config(bg=theme["success"], fg="white")
        self.reset_btn.config(bg=theme["danger"], fg="white")

        # Shortcuts Footer
        self.footer_label.config(bg=theme["bg"], fg=theme["secondary"])

        # Canvas redraws
        self.draw_progress()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    def change_theme_event(self, event):
        self.current_theme = self.theme_combo_var.get()
        self.apply_theme()

    def create_ui(self):
        # --- TITLE & SUBTITLE ---
        self.title_label = tk.Label(
            self.root,
            text="FOCUS & COUNTDOWN",
            font=("Helvetica", 22, "bold")
        )
        self.title_label.pack(pady=(15, 2))

        self.subtitle_label = tk.Label(
            self.root,
            text="High-Precision Productivity Desk",
            font=("Helvetica", 10, "italic")
        )
        self.subtitle_label.pack(pady=(0, 10))

        # --- TOP CONTROLS FRAME ---
        self.top_panel = tk.Frame(self.root)
        self.top_panel.pack(fill="x", padx=30, pady=5)

        # Mode Selection - Segmented Toggle Panel
        self.mode_timer_btn = tk.Button(
            self.top_panel,
            text="Standard Timer",
            font=("Helvetica", 9, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.toggle_mode(to_pomodoro=False)
        )
        self.mode_timer_btn.pack(side="left")

        self.mode_pomo_btn = tk.Button(
            self.top_panel,
            text="Pomodoro Mode",
            font=("Helvetica", 9, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.toggle_mode(to_pomodoro=True)
        )
        self.mode_pomo_btn.pack(side="left", padx=5)

        # Theme Dropdown Frame
        self.theme_label = tk.Label(
            self.top_panel,
            text="Theme:",
            font=("Helvetica", 9)
        )
        self.theme_label.pack(side="left", padx=(30, 5))

        self.theme_combo_var = tk.StringVar(value=self.current_theme)
        self.theme_dropdown = ttk.Combobox(
            self.top_panel,
            textvariable=self.theme_combo_var,
            values=list(self.THEMES.keys()),
            state="readonly",
            width=12
        )
        self.theme_dropdown.pack(side="left")
        self.theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme_event)

        # --- MAIN CARD SURFACE ---
        self.card = tk.Frame(self.root, bd=0)
        self.card.pack(padx=25, pady=10, fill="both", expand=True)

        # Progress Ring Canvas
        self.progress_canvas = tk.Canvas(
            self.card,
            width=220,
            height=220,
            highlightthickness=0
        )
        self.progress_canvas.pack(pady=(15, 5))

        # Prep variables for Canvas redraw tracking
        w, h = 220, 220
        cx, cy = w // 2, h // 2
        r = 90
        self.canvas_track = self.progress_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            width=8
        )
        self.canvas_arc = self.progress_canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90,
            extent=-360,
            width=12,
            style="arc"
        )
        self.canvas_text = self.progress_canvas.create_text(
            cx, cy,
            font=("Consolas", 32, "bold")
        )

        # Status & Activity Text
        self.status_label = tk.Label(
            self.card,
            text="Ready",
            font=("Helvetica", 11, "bold")
        )
        self.status_label.pack(pady=(2, 5))

        # Pomodoro specific indicators
        self.pomodoro_indicator_label = tk.Label(
            self.card,
            font=("Helvetica", 10, "bold")
        )
        self.pomo_dots_canvas = tk.Canvas(
            self.card,
            width=180,
            height=25,
            highlightthickness=0
        )

        # Timer Inputs Box
        self.timer_entry_label = tk.Label(
            self.card,
            text="Set Timer Interval:",
            font=("Helvetica", 10, "bold")
        )
        self.entry = tk.Entry(
            self.card,
            font=("Helvetica", 16),
            width=15,
            justify="center",
            relief="flat"
        )
        self.preset_tip_label = tk.Label(
            self.card,
            text="Format: SS | MM:SS | HH:MM:SS   •   [Right-click presets to delete]",
            font=("Helvetica", 8, "italic")
        )

        # Presets Outer Container Frame
        self.preset_frame = tk.Frame(self.card)

        # Sound Controls & Utility Card
        self.settings_card = tk.Frame(self.card)
        self.settings_card.pack(pady=5, fill="x", padx=30)

        self.tick_checkbox = tk.Checkbutton(
            self.settings_card,
            text="Clock Tick-Tock",
            variable=self.tick_sound_enabled,
            font=("Helvetica", 9),
            relief="flat",
            activeforeground="white",
            command=self.save_config
        )
        self.tick_checkbox.pack(side="left", padx=10)

        self.alert_label = tk.Label(
            self.settings_card,
            text="Alert Sound:",
            font=("Helvetica", 9)
        )
        self.alert_label.pack(side="left", padx=(20, 5))

        self.alert_dropdown = ttk.Combobox(
            self.settings_card,
            textvariable=self.alert_style,
            values=["Standard", "Chime", "Siren", "Silent"],
            state="readonly",
            width=9
        )
        self.alert_dropdown.pack(side="left")
        self.alert_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_config())

        # Control Buttons Tray
        self.button_frame = tk.Frame(self.card)
        self.button_frame.pack(pady=(15, 15))

        self.start_btn = tk.Button(
            self.button_frame,
            text="Start",
            width=9,
            height=2,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            command=self.start_timer
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            self.button_frame,
            text="Pause",
            width=9,
            height=2,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.pause_timer
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = tk.Button(
            self.button_frame,
            text="Resume",
            width=9,
            height=2,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.resume_timer
        )
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = tk.Button(
            self.button_frame,
            text="Reset",
            width=9,
            height=2,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            state="disabled",
            command=self.reset_timer
        )
        self.reset_btn.grid(row=0, column=3, padx=5)

        # Micro-animations
        self.add_hover(self.start_btn, "#3B82F6", "#2563EB")
        self.add_hover(self.pause_btn, "#F59E0B", "#D97706")
        self.add_hover(self.resume_btn, "#10B981", "#059669")
        self.add_hover(self.reset_btn, "#EF4444", "#DC2626")

        # --- FOOTER SHORTCUT REFERENCE ---
        self.footer_label = tk.Label(
            self.root,
            text="Spacebar → Play/Pause  |  R Key → Reset Timer",
            font=("Helvetica", 9, "bold")
        )
        self.footer_label.pack(side="bottom", pady=10)

    def render_preset_buttons(self):
        theme = self.THEMES[self.current_theme]
        # Clean current presets frame
        for child in self.preset_frame.winfo_children():
            child.destroy()

        # Render list of presets
        for text, value in self.presets:
            btn = tk.Button(
                self.preset_frame,
                text=text,
                bg=theme["button_bg"],
                fg=theme["button_fg"],
                activebackground=theme["primary"],
                activeforeground=theme["bg"],
                relief="flat",
                padx=8,
                pady=4,
                font=("Helvetica", 8, "bold"),
                cursor="hand2",
                command=lambda v=value: self.set_preset(v)
            )
            btn.pack(side="left", padx=3)
            # Bind right click to delete preset
            btn.bind("<Button-3>", lambda e, v=value: self.delete_preset(v))

        # Render Add Preset Button
        add_btn = tk.Button(
            self.preset_frame,
            text="+",
            bg=theme["primary"],
            fg=theme["bg"] if theme["bg"] != "#FFFFFF" else "white",
            relief="flat",
            padx=8,
            pady=4,
            font=("Helvetica", 8, "bold"),
            cursor="hand2",
            command=self.add_custom_preset
        )
        add_btn.pack(side="left", padx=5)


# ---------------- RUN APP ENTRY ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()