import tkinter as tk
from tkinter import simpledialog
import time
import winsound  # <- Built-in Windows sound

# ---------------------------- CONSTANTS ------------------------------- #
POMODOROS_PER_CYCLE = 4

MODES = {
    "focus": {"color": "#7c3aed", "label": "Focus Time"},
    "short_break": {"color": "#14b8a6", "label": "Short Break"},
    "long_break": {"color": "#4f46e5", "label": "Long Break"},
}

TIME_OPTIONS = [15, 25, 40, 50]  # Custom focus durations in minutes

# ---------------------------- TIMER CLASS ----------------------------- #
class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x550")
        self.root.configure(bg="#f3f4f6")
        
        self.session_count = 0
        self.is_active = False
        self.current_mode = "focus"
        self.task_name = ""
        self.timer_seconds = 25 * 60
        self.initial_seconds = self.timer_seconds
        self.interval_id = None

        # ---------- UI ELEMENTS ---------- #
        self.canvas = tk.Canvas(root, width=300, height=300, bg="#f3f4f6", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.circle = self.canvas.create_oval(10, 10, 290, 290, width=10, outline="#d1d5db")
        self.arc = self.canvas.create_arc(10, 10, 290, 290, start=90, extent=0, width=10, outline=MODES[self.current_mode]["color"], style="arc")
        self.task_text = self.canvas.create_text(150, 120, text="No Task", font=("Helvetica", 14, "bold"), fill="#111827")
        self.time_text = self.canvas.create_text(150, 170, text=self.format_time(self.timer_seconds), font=("Courier", 36, "bold"), fill="#111827")

        self.phase_label = tk.Label(root, text=MODES[self.current_mode]["label"], font=("Helvetica", 14), bg="#f3f4f6")
        self.phase_label.pack(pady=5)

        self.session_label = tk.Label(root, text=f"Session: {self.session_count}", font=("Helvetica", 12), bg="#f3f4f6")
        self.session_label.pack(pady=5)

        # Buttons
        self.button_frame = tk.Frame(root, bg="#f3f4f6")
        self.button_frame.pack(pady=10)

        self.start_btn = tk.Button(self.button_frame, text="Start", bg="#22c55e", fg="white", width=10, command=self.toggle_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.skip_btn = tk.Button(self.button_frame, text="Skip", bg="#facc15", width=10, command=self.skip_phase)
        self.skip_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(self.button_frame, text="Reset", bg="#9ca3af", width=10, command=self.reset_timer)
        self.reset_btn.grid(row=0, column=2, padx=5)

        self.task_btn = tk.Button(root, text="Set Task", bg="#ec4899", fg="white", command=self.set_task)
        self.task_btn.pack(pady=10)

        # Time selection buttons
        self.time_frame = tk.Frame(root, bg="#f3f4f6")
        self.time_frame.pack(pady=10)
        for t in TIME_OPTIONS:
            tk.Button(self.time_frame, text=f"{t} min", width=6, command=lambda m=t: self.set_custom_time(m)).pack(side="left", padx=5)

        self.update_display()

    # -------------------- TIMER FUNCTIONS -------------------- #
    def format_time(self, total_seconds):
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_display(self):
        self.canvas.itemconfig(self.time_text, text=self.format_time(self.timer_seconds))
        self.canvas.itemconfig(self.task_text, text=self.task_name or "No Task")
        self.phase_label.config(text=MODES[self.current_mode]["label"])
        self.session_label.config(text=f"Session: {self.session_count}")
        ratio = self.timer_seconds / self.initial_seconds
        self.canvas.itemconfig(self.arc, extent=-360 * ratio, outline=MODES[self.current_mode]["color"])

    def timer_tick(self):
        if self.is_active:
            if self.timer_seconds > 0:
                self.timer_seconds -= 1
                self.update_display()
                self.interval_id = self.root.after(1000, self.timer_tick)
            else:
                self.next_phase()

    def toggle_timer(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.start_btn.config(text="Pause", bg="#facc15")
            self.timer_tick()
        else:
            self.start_btn.config(text="Start", bg="#22c55e")
            if self.interval_id:
                self.root.after_cancel(self.interval_id)
                self.interval_id = None

    # -------------------- PLAY ALARM -------------------- #
    def play_alarm(self):
        # Windows beep: 2500Hz for 1 second, repeated 3 times
        for _ in range(3):
            winsound.Beep(2500, 1000)

    def next_phase(self):
        self.is_active = False
        self.start_btn.config(text="Start", bg="#22c55e")
        self.play_alarm()  # Play sound when timer ends

        if self.current_mode == "focus":
            self.session_count += 1
            if self.session_count % POMODOROS_PER_CYCLE == 0:
                self.current_mode = "long_break"
                self.timer_seconds = 15 * 60
            else:
                self.current_mode = "short_break"
                self.timer_seconds = 5 * 60
        else:
            self.current_mode = "focus"
            self.timer_seconds = 25 * 60

        self.initial_seconds = self.timer_seconds
        self.update_display()
        self.toggle_timer()

    def skip_phase(self):
        if self.interval_id:
            self.root.after_cancel(self.interval_id)
            self.interval_id = None
        self.next_phase()

    def reset_timer(self):
        if self.interval_id:
            self.root.after_cancel(self.interval_id)
            self.interval_id = None
        self.current_mode = "focus"
        self.timer_seconds = 25 * 60
        self.initial_seconds = self.timer_seconds
        self.session_count = 0
        self.is_active = False
        self.start_btn.config(text="Start", bg="#22c55e")
        self.update_display()

    def set_task(self):
        task = simpledialog.askstring("New Task", "What are you working on?")
        if task:
            self.task_name = task
            self.update_display()

    def set_custom_time(self, minutes):
        self.timer_seconds = minutes * 60
        self.initial_seconds = self.timer_seconds
        self.current_mode = "focus"
        self.is_active = False
        self.start_btn.config(text="Start", bg="#22c55e")
        self.update_display()


# ---------------------------- RUN APP ------------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
