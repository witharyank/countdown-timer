# ⏳ Modern Countdown Timer

A premium, high-fidelity desktop productivity countdown timer built with Python and Tkinter. Featuring a sleek, Tailwind CSS-inspired dark mode UI, smooth visual animations, customized presets, and sound alerts.

![Countdown Timer Preview](assets/timer_mockup.png)

---

## ✨ Features

- **🎨 Modern Dark Theme**: Built with a beautiful slate-blue palette (`#0F172A` background and `#111827` active card surface), consistent typography, and reactive interactive components.
- **⚡ Quick-Preset Buttons**: One-tap buttons for rapid scheduling of standard intervals (1 Min, 5 Min, 10 Min, and 25 Min - perfect for Pomodoro sessions).
- **⏱️ Flexible Time Input**: Smart input parser supporting multiple formats:
  - `SS` (e.g., `90` -> `00:01:30`)
  - `MM:SS` (e.g., `05:00` -> `00:05:00`)
  - `HH:MM:SS` (e.g., `01:30:00`)
- **📊 Real-time Progress Tracking**: Features a high-contrast progress bar that fills up dynamically as time ticks away.
- **⚠️ Low-Time Alert**: Countdown text transitions to a warnings-danger red (`#EF4444`) when less than 10 seconds remain.
- **🔔 Completion Effects**:
  - **Flash Animation**: Beautiful, fast text-flashing effect on completion.
  - **Acoustic Sound Alert**: Plays 3 beeps on Windows (utilizing `winsound`) or a system bell sound fallback on macOS/Linux.
- **⌨️ Keyboard Shortcuts**: Complete hands-free keyboard controls.

---

## ⌨️ Keyboard Shortcuts

Easily control the timer without lifting your hands from the keyboard:

| Action | Shortcut Key | Description |
| :--- | :---: | :--- |
| **Start / Resume** | `Enter` | Starts the timer or resumes from pause |
| **Pause** | `Spacebar` | Temporarily pauses a running countdown |
| **Reset** | `R` | Resets the timer back to its initial ready state |

---

## 🛠️ Tech Stack & Requirements

- **Python 3.10+** (Tested with Python 3.11/3.12)
- **Tkinter** & **ttk** (Python's native GUI framework)
- **Platform Compatibility**: 
  - 🖥️ **Windows**: Plays premium acoustic beeps via native `winsound`.
  - 🍎 **macOS / 🐧 Linux**: Plays standard system audio notifications via bell fallbacks.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/witharyank/countdown-timer.git
cd countdown-timer
```

### 2. Run the Application
Since this application utilizes Python's built-in standard libraries (`tkinter` and `winsound`/`sys`), **no external dependencies or virtual environments are required**! Simply run:

```bash
python countdown.py
```

---

## 📂 Code Architecture

The timer is structured in a single clean, object-oriented module (`countdown.py`):

- **`CountdownTimer` Class**: Encapsulates the complete application state, GUI frame creation, styling engines, and interaction loops.
- **Input Sanitization (`sanitize_time_input`)**: Normalizes arbitrary raw input formats into precise seconds, managing carries seamlessly.
- **Visual Engines**:
  - **`countdown`**: Runs at a steady $1\text{Hz}$ using Tkinter's event scheduling (`after` system).
  - **`flash` / `flash_animation`**: Implements asynchronous canvas highlight toggling for completion effects.
- **Event Listeners**: Sets up robust key bindings and hover effects on buttons for enhanced desktop usability.
