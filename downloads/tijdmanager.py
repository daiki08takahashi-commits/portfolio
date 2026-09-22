# -*- coding: utf-8 -*-
"""TIJDMANAGER - a gentle time management desktop app.

Run with:
    python tijdmanager.py

The app stores local data in tijdmanager_data.json beside this file.
"""

from __future__ import annotations

import json
import math
import textwrap
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "tijdmanager_data.json"
LOGO_FILE = APP_DIR / "assets" / "logo.png"

CYAN = "#02B2E4"
CYAN_DARK = "#008BB7"
LIME = "#CED200"
LIME_SOFT = "#F2F4A8"
PAPER = "#FFFFFF"
WASH = "#F5FAFB"
INK = "#22252D"
MUTED = "#68717C"
LINE = "#DDE7EC"
CORAL = "#FF6B6B"
VIOLET = "#7158E2"
GREEN = "#14A76C"
AMBER = "#F2A900"

BLOCK_COLOURS = {
    "Study": CYAN,
    "Work": VIOLET,
    "Break": GREEN,
    "Exercise": CORAL,
    "Rest": LIME,
}

LANGUAGES = [
    "English (UK)",
    "Français",
    "Nederlands",
    "Eesti",
    "Deutsch",
    "Suomi",
    "Svenska",
]


def today_key() -> str:
    return date.today().isoformat()


def day_key(days_from_today: int) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()


def new_id() -> str:
    return uuid.uuid4().hex[:10]


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def merge_defaults(defaults, loaded):
    if isinstance(defaults, dict) and isinstance(loaded, dict):
        merged = dict(defaults)
        for key, value in loaded.items():
            merged[key] = merge_defaults(defaults.get(key), value)
        return merged
    return loaded if loaded is not None else defaults


def default_state() -> dict:
    return {
        "xp": 140,
        "settings": {
            "language": "English (UK)",
            "dark_mode": False,
            "low_stimulation": False,
            "high_contrast": False,
            "reduce_animations": False,
            "sound": False,
        },
        "timer": {
            "mode": "25/5",
            "focus_minutes": 25,
            "break_minutes": 5,
            "phase": "Focus",
            "seconds_left": 25 * 60,
            "total_seconds": 25 * 60,
            "running": False,
            "task": "Study session",
        },
        "tasks": [
            {
                "id": new_id(),
                "title": "Read one chapter",
                "priority": "Important",
                "subject": "Psychology",
                "done": False,
                "created": today_key(),
            },
            {
                "id": new_id(),
                "title": "Prepare tomorrow's bag",
                "priority": "Optional",
                "subject": "Routine",
                "done": False,
                "created": today_key(),
            },
            {
                "id": new_id(),
                "title": "Email tutor about deadline",
                "priority": "Urgent",
                "subject": "Admin",
                "done": False,
                "created": today_key(),
            },
        ],
        "study_logs": [
            {"id": new_id(), "date": day_key(-6), "minutes": 25, "subject": "Maths", "target_start": "10:00", "target_end": "10:30"},
            {"id": new_id(), "date": day_key(-5), "minutes": 55, "subject": "Essay", "target_start": "15:00", "target_end": "16:00"},
            {"id": new_id(), "date": day_key(-4), "minutes": 30, "subject": "Biology", "target_start": "09:30", "target_end": "10:00"},
            {"id": new_id(), "date": day_key(-2), "minutes": 70, "subject": "Maths", "target_start": "11:00", "target_end": "12:10"},
            {"id": new_id(), "date": day_key(-1), "minutes": 40, "subject": "Essay", "target_start": "17:00", "target_end": "17:45"},
        ],
        "checkins": {
            day_key(-2): {"mood": "Good", "energy": 7, "stress": 4},
            day_key(-1): {"mood": "Okay", "energy": 5, "stress": 6},
        },
        "planner_blocks": [
            {"id": new_id(), "date": today_key(), "hour": 9, "type": "Study"},
            {"id": new_id(), "date": today_key(), "hour": 11, "type": "Break"},
            {"id": new_id(), "date": today_key(), "hour": 14, "type": "Work"},
        ],
        "deadlines": [
            {"id": new_id(), "title": "Essay draft", "date": day_key(1), "type": "Assignment"},
            {"id": new_id(), "title": "Exam review", "date": day_key(7), "type": "Exam"},
        ],
        "distractions": [
            {"id": new_id(), "date": day_key(-1), "type": "YouTube", "minutes": 18, "note": "Opened during break and stayed"},
        ],
        "routines": {
            "morning": [
                {"id": new_id(), "title": "Wake up", "done": False},
                {"id": new_id(), "title": "Breakfast", "done": False},
                {"id": new_id(), "title": "Medication", "done": False},
                {"id": new_id(), "title": "Study", "done": False},
            ],
            "evening": [
                {"id": new_id(), "title": "Review tasks", "done": False},
                {"id": new_id(), "title": "Prepare tomorrow", "done": False},
            ],
        },
        "journal": {},
        "reminders": [
            {"id": new_id(), "time": "09:00", "text": "You planned 30 minutes today. Want to begin?", "fired_on": ""},
        ],
        "partner": {"name": "", "email": ""},
        "chat": [
            {"role": "coach", "text": "Tell me what feels hard today, and I will suggest one smaller next move."},
        ],
        "last_breakdown": [],
    }


class ScrollPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, bg=WASH, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=WASH)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._resize_scrollregion)
        self.canvas.bind("<Configure>", self._resize_window)

    def _resize_scrollregion(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_window(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()


class TijdmanagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TIJDMANAGER")
        self.geometry("1160x780")
        self.minsize(940, 640)
        self.state_data = self.load_state()
        self.logo_image = None
        self.status_var = tk.StringVar(value="Would now be a good time to begin?")
        self.mode_var = tk.StringVar(value=self.state_data["timer"]["mode"])
        self.task_var = tk.StringVar(value=self.state_data["timer"]["task"])
        self.energy_var = tk.IntVar(value=self.today_checkin().get("energy", 6))
        self.stress_var = tk.IntVar(value=self.today_checkin().get("stress", 4))
        self.mood_var = tk.StringVar(value=self.today_checkin().get("mood", "Okay"))
        self.selected_block_var = tk.StringVar(value="Study")
        self.hour_var = tk.IntVar(value=9)
        self.language_var = tk.StringVar(value=self.state_data["settings"].get("language", "English (UK)"))
        self.setup_style()
        self.build_layout()
        self.refresh_all()
        self.after(1000, self.tick_timer)
        self.after(30000, self.check_reminders)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_state(self) -> dict:
        defaults = default_state()
        if not DATA_FILE.exists():
            return defaults
        try:
            with DATA_FILE.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            return merge_defaults(defaults, loaded)
        except (OSError, json.JSONDecodeError):
            return defaults

    def save_state(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", encoding="utf-8") as handle:
            json.dump(self.state_data, handle, indent=2, ensure_ascii=False)

    def setup_style(self):
        self.configure(bg=WASH)
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=WASH, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", PAPER)], foreground=[("selected", CYAN_DARK)])
        style.configure("TButton", padding=(10, 7), font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background=CYAN, foreground=INK, bordercolor=CYAN)
        style.configure("Soft.TButton", background=LIME_SOFT, foreground=INK, bordercolor=LIME)
        style.configure("TCombobox", padding=6)

    def build_layout(self):
        header = tk.Frame(self, bg=PAPER, highlightbackground=LINE, highlightthickness=1, padx=14, pady=10)
        header.pack(fill="x", padx=12, pady=(12, 8))

        if LOGO_FILE.exists():
            try:
                original = tk.PhotoImage(file=str(LOGO_FILE))
                self.logo_image = original.subsample(max(1, original.width() // 64), max(1, original.height() // 64))
                tk.Label(header, image=self.logo_image, bg=PAPER).pack(side="left", padx=(0, 12))
            except tk.TclError:
                self.logo_image = None

        title_box = tk.Frame(header, bg=PAPER)
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(title_box, text="TIJDMANAGER", bg=PAPER, fg=INK, font=("Segoe UI Black", 20)).pack(anchor="w")
        tk.Label(title_box, text="Gentle focus, real progress", bg=PAPER, fg=MUTED).pack(anchor="w")

        ttk.Label(header, text="Language").pack(side="left", padx=(10, 4))
        language = ttk.Combobox(header, textvariable=self.language_var, values=LANGUAGES, state="readonly", width=16)
        language.pack(side="left")
        language.bind("<<ComboboxSelected>>", lambda _event: self.update_language())

        ttk.Button(header, text="Help me focus", style="Accent.TButton", command=self.emergency_focus).pack(side="left", padx=(10, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.pages = {}
        for key, label in [
            ("today", "Today"),
            ("planner", "Planner"),
            ("analytics", "Analytics"),
            ("assistant", "Assistant"),
            ("routines", "Routines"),
            ("reports", "Reports"),
            ("settings", "Settings"),
        ]:
            page = ScrollPage(self.notebook)
            self.pages[key] = page
            self.notebook.add(page, text=label)

    def panel(self, parent, title: str, subtitle: str = "") -> tk.Frame:
        frame = tk.Frame(parent, bg=PAPER, highlightbackground=LINE, highlightthickness=1, padx=14, pady=12)
        tk.Label(frame, text=subtitle, bg=PAPER, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(frame, text=title, bg=PAPER, fg=INK, font=("Segoe UI", 18, "bold"), wraplength=420, justify="left").pack(anchor="w", pady=(0, 10))
        return frame

    def make_entry(self, parent, width=18, textvariable=None):
        entry = ttk.Entry(parent, width=width, textvariable=textvariable)
        return entry

    def refresh_all(self):
        self.build_today_page()
        self.build_planner_page()
        self.build_analytics_page()
        self.build_assistant_page()
        self.build_routines_page()
        self.build_reports_page()
        self.build_settings_page()
        self.draw_timer()
        self.save_state()

    def build_today_page(self):
        page = self.pages["today"]
        page.clear()
        body = page.inner
        body.columnconfigure((0, 1, 2), weight=1, uniform="today")

        timer_panel = self.panel(body, "Ready when you are", "Focus Session Timer")
        timer_panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        top = tk.Frame(timer_panel, bg=PAPER)
        top.pack(fill="x")
        ttk.Button(top, text="Continue session", style="Soft.TButton", command=self.continue_session).pack(side="right")
        self.timer_canvas = tk.Canvas(timer_panel, width=260, height=260, bg=PAPER, highlightthickness=0)
        self.timer_canvas.pack(pady=6)
        ttk.Label(timer_panel, text="Current task").pack(anchor="w")
        task_entry = ttk.Entry(timer_panel, textvariable=self.task_var)
        task_entry.pack(fill="x", pady=(2, 8))
        task_entry.bind("<KeyRelease>", lambda _event: self.update_timer_task())
        mode_row = tk.Frame(timer_panel, bg=PAPER)
        mode_row.pack(fill="x", pady=(0, 8))
        mode_box = ttk.Combobox(mode_row, textvariable=self.mode_var, values=["25/5", "50/10", "Custom"], state="readonly", width=10)
        mode_box.pack(side="left", padx=(0, 8))
        mode_box.bind("<<ComboboxSelected>>", lambda _event: self.change_timer_mode())
        self.custom_focus = ttk.Spinbox(mode_row, from_=5, to=180, width=6)
        self.custom_focus.set(self.state_data["timer"]["focus_minutes"])
        self.custom_focus.pack(side="left", padx=4)
        self.custom_break = ttk.Spinbox(mode_row, from_=1, to=60, width=6)
        self.custom_break.set(self.state_data["timer"]["break_minutes"])
        self.custom_break.pack(side="left", padx=4)
        ttk.Button(mode_row, text="Apply", command=self.apply_custom_timer).pack(side="left", padx=4)
        controls = tk.Frame(timer_panel, bg=PAPER)
        controls.pack(fill="x", pady=6)
        ttk.Button(controls, text="▶ Start", style="Accent.TButton", command=self.start_timer).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(controls, text="Ⅱ Pause", style="Soft.TButton", command=self.pause_timer).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(controls, text="↺ Reset", command=self.reset_timer).pack(side="left", expand=True, fill="x", padx=2)
        tk.Label(timer_panel, textvariable=self.status_var, bg=PAPER, fg=MUTED, wraplength=350, justify="left").pack(anchor="w", pady=(8, 0))

        tasks_panel = self.panel(body, "Today", "Daily plan")
        tasks_panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        xp = self.state_data.get("xp", 0)
        tk.Label(tasks_panel, text=f"{xp} XP · Level {xp // 100 + 1} · {self.streak()} day streak", bg=LIME_SOFT, fg=INK, padx=10, pady=4).pack(anchor="e")
        add_row = tk.Frame(tasks_panel, bg=PAPER)
        add_row.pack(fill="x", pady=(6, 8))
        self.task_title_entry = ttk.Entry(add_row, width=24)
        self.task_title_entry.insert(0, "")
        self.task_title_entry.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.task_priority_var = tk.StringVar(value="Important")
        ttk.Combobox(add_row, textvariable=self.task_priority_var, values=["Urgent", "Important", "Optional"], state="readonly", width=11).pack(side="left", padx=4)
        self.task_subject_entry = ttk.Entry(add_row, width=12)
        self.task_subject_entry.pack(side="left", padx=4)
        ttk.Button(add_row, text="+", style="Accent.TButton", command=self.add_task).pack(side="left")
        self.task_list_frame = tk.Frame(tasks_panel, bg=PAPER)
        self.task_list_frame.pack(fill="both", expand=True)
        self.render_tasks()
        self.build_study_log(tasks_panel)

        mood_panel = self.panel(body, "Check-in", "Mood & energy")
        mood_panel.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)
        moods = tk.Frame(mood_panel, bg=PAPER)
        moods.pack(fill="x")
        for mood in ["😀 Great", "🙂 Good", "😐 Okay", "😞 Difficult"]:
            clean = mood.split(" ", 1)[1]
            ttk.Radiobutton(moods, text=mood, value=clean, variable=self.mood_var).pack(side="left", expand=True, padx=2)
        self.scale_row(mood_panel, "Energy", self.energy_var)
        self.scale_row(mood_panel, "Stress", self.stress_var)
        ttk.Button(mood_panel, text="Save check-in", style="Accent.TButton", command=self.save_checkin).pack(fill="x", pady=8)
        tk.Label(mood_panel, text=self.burnout_text(), bg="#EAF8FC", fg=INK, padx=10, pady=8, wraplength=320, justify="left").pack(fill="x")

        insight_panel = self.panel(body, "Weak point & next step", "AI analysis")
        insight_panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        tk.Label(insight_panel, text=self.insight_text(), bg="#EAF8FC", fg=INK, padx=10, pady=8, wraplength=340, justify="left").pack(fill="x")

        reminder_panel = self.panel(body, "Gentle prompts", "Smart reminders")
        reminder_panel.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.build_reminders(reminder_panel)

        metrics_panel = self.panel(body, "Weekly progress", "Quick metrics")
        metrics_panel.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)
        for label, value in [
            ("Weekly hours", f"{self.total_minutes_since(7) / 60:.1f}h"),
            ("Completion", f"{self.completion_rate()}%"),
            ("Focus score", str(self.focus_score())),
        ]:
            tk.Label(metrics_panel, text=f"{label}: {value}", bg=PAPER, fg=INK, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=5)

    def build_study_log(self, parent):
        box = tk.Frame(parent, bg=PAPER)
        box.pack(fill="x", pady=(12, 0))
        tk.Label(box, text="Daily studying time", bg=PAPER, fg=INK, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        row = tk.Frame(box, bg=PAPER)
        row.pack(fill="x", pady=5)
        self.study_minutes_entry = ttk.Entry(row, width=9)
        self.study_minutes_entry.pack(side="left", padx=(0, 4))
        self.study_subject_entry = ttk.Entry(row, width=14)
        self.study_subject_entry.pack(side="left", padx=4)
        self.target_start_entry = ttk.Entry(row, width=8)
        self.target_start_entry.insert(0, "09:00")
        self.target_start_entry.pack(side="left", padx=4)
        self.target_end_entry = ttk.Entry(row, width=8)
        self.target_end_entry.insert(0, "10:00")
        self.target_end_entry.pack(side="left", padx=4)
        ttk.Button(row, text="Record", style="Soft.TButton", command=self.add_study_log).pack(side="left", padx=4)

    def scale_row(self, parent, label, variable):
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, bg=PAPER, fg=INK, width=8, anchor="w").pack(side="left")
        tk.Scale(row, from_=1, to=10, orient="horizontal", variable=variable, bg=PAPER, highlightthickness=0, troughcolor=LINE, activebackground=CYAN).pack(side="left", expand=True, fill="x")
        tk.Label(row, textvariable=variable, bg=PAPER, fg=INK, width=3).pack(side="right")

    def render_tasks(self):
        for child in self.task_list_frame.winfo_children():
            child.destroy()
        if not self.state_data["tasks"]:
            tk.Label(self.task_list_frame, text="No tasks yet.", bg=PAPER, fg=MUTED).pack(anchor="w", pady=6)
            return
        for task in self.state_data["tasks"][:10]:
            row = tk.Frame(self.task_list_frame, bg=WASH, highlightbackground=LINE, highlightthickness=1, padx=8, pady=6)
            row.pack(fill="x", pady=4)
            var = tk.BooleanVar(value=task.get("done", False))
            ttk.Checkbutton(row, variable=var, command=lambda item=task, value=var: self.toggle_task(item, value)).pack(side="left")
            text = f"{task['title']}  ·  {task['priority']}  ·  {task.get('subject', 'General')}"
            style = ("Segoe UI", 10, "overstrike") if task.get("done") else ("Segoe UI", 10, "bold")
            tk.Label(row, text=text, bg=WASH, fg=INK, font=style, anchor="w", wraplength=430, justify="left").pack(side="left", fill="x", expand=True)
            ttk.Button(row, text="×", width=3, command=lambda item=task: self.remove_task(item)).pack(side="right")

    def build_reminders(self, parent):
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x")
        self.reminder_time_entry = ttk.Entry(row, width=8)
        self.reminder_time_entry.insert(0, "09:00")
        self.reminder_time_entry.pack(side="left", padx=(0, 4))
        self.reminder_text_entry = ttk.Entry(row)
        self.reminder_text_entry.insert(0, "Would now be a good time to start?")
        self.reminder_text_entry.pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(row, text="+", style="Soft.TButton", command=self.add_reminder).pack(side="left")
        for reminder in self.state_data["reminders"]:
            tk.Label(parent, text=f"{reminder['time']}  {reminder['text']}", bg=PAPER, fg=INK, anchor="w", wraplength=420, justify="left").pack(fill="x", pady=4)

    def build_planner_page(self):
        page = self.pages["planner"]
        page.clear()
        body = page.inner
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)

        controls = self.panel(body, "Blocks", "Time Blocking Planner")
        controls.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tk.Label(controls, text="Choose a block and hour, then add it to today.", bg=PAPER, fg=MUTED, wraplength=350, justify="left").pack(anchor="w")
        ttk.Combobox(controls, textvariable=self.selected_block_var, values=list(BLOCK_COLOURS), state="readonly").pack(fill="x", pady=6)
        ttk.Spinbox(controls, from_=6, to=22, textvariable=self.hour_var).pack(fill="x", pady=6)
        ttk.Button(controls, text="Add time block", style="Accent.TButton", command=self.add_time_block).pack(fill="x", pady=4)
        tk.Label(controls, text="Daily studying target time", bg=PAPER, fg=INK, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 2))
        tk.Label(controls, text=self.target_time_summary(), bg=PAPER, fg=CYAN_DARK, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.build_deadline_editor(controls)

        timeline = self.panel(body, "Today timeline", "Click × to remove a block")
        timeline.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        for hour in range(6, 23):
            row = tk.Frame(timeline, bg=WASH, highlightbackground=LINE, highlightthickness=1, padx=6, pady=5)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{hour:02}:00", bg=WASH, fg=MUTED, width=7).pack(side="left")
            blocks = [item for item in self.state_data["planner_blocks"] if item["date"] == today_key() and item["hour"] == hour]
            for block in blocks:
                tk.Label(row, text=block["type"], bg=BLOCK_COLOURS.get(block["type"], LINE), fg=INK if block["type"] in ("Study", "Rest") else "white", padx=10, pady=4).pack(side="left", padx=3)
                ttk.Button(row, text="×", width=3, command=lambda item=block: self.remove_block(item)).pack(side="left")

        calendar = self.panel(body, "Calendar", "Study logs and deadlines")
        calendar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self.build_calendar(calendar)

    def build_deadline_editor(self, parent):
        tk.Label(parent, text="Deadlines", bg=PAPER, fg=INK, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 2))
        self.deadline_title_entry = ttk.Entry(parent)
        self.deadline_title_entry.pack(fill="x", pady=3)
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x")
        self.deadline_date_entry = ttk.Entry(row, width=12)
        self.deadline_date_entry.insert(0, day_key(7))
        self.deadline_date_entry.pack(side="left", padx=(0, 4))
        self.deadline_type_var = tk.StringVar(value="Assignment")
        ttk.Combobox(row, textvariable=self.deadline_type_var, values=["Assignment", "Exam", "Work"], state="readonly", width=12).pack(side="left", padx=4)
        ttk.Button(row, text="Add", style="Soft.TButton", command=self.add_deadline).pack(side="left", padx=4)
        for item in sorted(self.state_data["deadlines"], key=lambda x: x["date"]):
            days = (parse_day(item["date"]) - date.today()).days
            text = f"{item['title']} · {item['type']} · {self.days_label(days)} · {self.schedule_suggestion(days)}"
            tk.Label(parent, text=text, bg=PAPER, fg=INK, wraplength=350, justify="left").pack(anchor="w", pady=3)

    def build_calendar(self, parent):
        now = date.today().replace(day=1)
        header = now.strftime("%B %Y")
        tk.Label(parent, text=header, bg=PAPER, fg=INK, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 6))
        grid = tk.Frame(parent, bg=PAPER)
        grid.pack(fill="x")
        for index, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            tk.Label(grid, text=name, bg=LIME_SOFT, fg=INK, width=15, padx=4, pady=4).grid(row=0, column=index, sticky="nsew", padx=1, pady=1)
            grid.columnconfigure(index, weight=1)
        first_weekday = now.weekday()
        days = (date(now.year + (now.month // 12), (now.month % 12) + 1, 1) - timedelta(days=1)).day
        for day in range(1, days + 1):
            key = date(now.year, now.month, day).isoformat()
            row = (day + first_weekday - 1) // 7 + 1
            col = (day + first_weekday - 1) % 7
            minutes = self.total_minutes_for_date(key)
            deadline = next((item for item in self.state_data["deadlines"] if item["date"] == key), None)
            label = f"{day}"
            if minutes:
                label += f"\n{minutes}m"
            if deadline:
                label += f"\n{deadline['title'][:12]}"
            bg = "#EAF8FC" if key == today_key() else WASH
            tk.Label(grid, text=label, bg=bg, fg=INK, width=15, height=4, justify="left", anchor="nw", padx=4, pady=4, highlightbackground=LINE, highlightthickness=1).grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

    def build_analytics_page(self):
        page = self.pages["analytics"]
        page.clear()
        body = page.inner
        body.columnconfigure((0, 1), weight=1, uniform="analytics")

        daily = self.panel(body, "Daily hours", "Study Analytics Dashboard")
        daily.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        canvas = tk.Canvas(daily, width=500, height=230, bg=PAPER, highlightthickness=0)
        canvas.pack(fill="x")
        self.draw_bar_chart(canvas)

        subjects = self.panel(body, "Subject breakdown", "Pie chart")
        subjects.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        pie = tk.Canvas(subjects, width=500, height=230, bg=PAPER, highlightthickness=0)
        pie.pack(fill="x")
        self.draw_pie_chart(pie)

        heat = self.panel(body, "Heatmap", "Last 35 days")
        heat.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.draw_heatmap(heat)

        log = self.panel(body, "Study log", "Daily studying time column")
        log.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        for entry in self.state_data["study_logs"][:18]:
            text = f"{entry['date']} · {entry['minutes']} min · {entry.get('target_start', '--')}-{entry.get('target_end', '--')} · {entry['subject']}"
            tk.Label(log, text=text, bg=PAPER, fg=INK, anchor="w").pack(fill="x", pady=2)

        badges = self.panel(body, "Achievements", "Reward & Gamification System")
        badges.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self.build_badges(badges)

    def draw_bar_chart(self, canvas):
        days = list(reversed(self.daily_totals(14)))
        max_minutes = max([60] + [item["minutes"] for item in days])
        width, height = 500, 210
        bar_space = width / len(days)
        for index, item in enumerate(days):
            bar_height = max(5, item["minutes"] / max_minutes * 170)
            x1 = index * bar_space + 10
            y1 = height - bar_height - 20
            x2 = x1 + bar_space - 8
            y2 = height - 20
            canvas.create_rectangle(x1, y1, x2, y2, fill=CYAN, outline="")
            canvas.create_text((x1 + x2) / 2, y1 - 10, text=f"{item['minutes'] // 60}h", fill=MUTED, font=("Segoe UI", 8))
        canvas.create_line(8, height - 20, width - 8, height - 20, fill=LINE)

    def draw_pie_chart(self, canvas):
        totals = defaultdict(int)
        for entry in self.state_data["study_logs"]:
            totals[entry.get("subject", "Study")] += int(entry["minutes"])
        if not totals:
            canvas.create_text(250, 100, text="No study data yet", fill=MUTED)
            return
        colours = [CYAN, LIME, VIOLET, CORAL, GREEN, AMBER]
        total = sum(totals.values())
        start = 0
        for index, (subject, minutes) in enumerate(sorted(totals.items(), key=lambda x: x[1], reverse=True)):
            extent = minutes / total * 360
            canvas.create_arc(30, 20, 210, 200, start=start, extent=extent, fill=colours[index % len(colours)], outline=PAPER)
            canvas.create_rectangle(250, 32 + index * 26, 266, 48 + index * 26, fill=colours[index % len(colours)], outline="")
            canvas.create_text(276, 40 + index * 26, text=f"{subject}: {minutes}m", anchor="w", fill=INK, font=("Segoe UI", 10))
            start += extent

    def draw_heatmap(self, parent):
        frame = tk.Frame(parent, bg=PAPER)
        frame.pack(anchor="w")
        for index, item in enumerate(reversed(self.daily_totals(35))):
            level = 0
            if item["minutes"] >= 120:
                level = 4
            elif item["minutes"] >= 60:
                level = 3
            elif item["minutes"] >= 25:
                level = 2
            elif item["minutes"] > 0:
                level = 1
            colours = [LINE, "#BFEAF5", "#70D4EC", LIME_SOFT, LIME]
            tk.Label(frame, text=parse_day(item["date"]).day, bg=colours[level], fg=INK, width=5, height=2).grid(row=index // 7, column=index % 7, padx=3, pady=3)

    def build_badges(self, parent):
        total_hours = sum(int(item["minutes"]) for item in self.state_data["study_logs"]) / 60
        badges = [
            ("First Study Session", bool(self.state_data["study_logs"])),
            ("7-Day Streak", self.streak() >= 7),
            ("100 Hours Studied", total_hours >= 100),
            ("Journal Keeper", len(self.state_data["journal"]) >= 3),
            ("Focus Saver", self.focus_score() >= 70),
        ]
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x")
        for label, unlocked in badges:
            bg = LIME_SOFT if unlocked else WASH
            mark = "✓" if unlocked else "○"
            tk.Label(row, text=f"{mark} {label}", bg=bg, fg=INK, padx=12, pady=8, highlightbackground=LINE, highlightthickness=1).pack(side="left", padx=4, pady=4)

    def build_assistant_page(self):
        page = self.pages["assistant"]
        page.clear()
        body = page.inner
        body.columnconfigure((0, 1), weight=1, uniform="assistant")

        breakdown = self.panel(body, "Break a task down", "Executive Function Assistant")
        breakdown.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.breakdown_entry = ttk.Entry(breakdown)
        self.breakdown_entry.insert(0, "Write essay")
        self.breakdown_entry.pack(fill="x", pady=4)
        ttk.Button(breakdown, text="Break into steps", style="Accent.TButton", command=self.break_task_down).pack(fill="x", pady=4)
        self.steps_frame = tk.Frame(breakdown, bg=PAPER)
        self.steps_frame.pack(fill="x", pady=8)
        self.render_steps()
        ttk.Button(breakdown, text="Add steps to to-do list", style="Soft.TButton", command=self.add_steps_to_tasks).pack(fill="x")

        goals = self.panel(body, "Minimum, target, stretch", "Adaptive Goal Setting")
        goals.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        row = tk.Frame(goals, bg=PAPER)
        row.pack(fill="x")
        self.goal_minutes_entry = ttk.Entry(row, width=10)
        self.goal_minutes_entry.insert(0, "240")
        self.goal_minutes_entry.pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Suggest goals", style="Soft.TButton", command=self.suggest_goals).pack(side="left")
        self.goal_text = tk.Text(goals, height=8, wrap="word", bg="#EAF8FC", fg=INK, relief="flat")
        self.goal_text.pack(fill="x", pady=8)
        self.suggest_goals()

        chat = self.panel(body, "Coach", "Study prowess chatbot")
        chat.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.chat_text = tk.Text(chat, height=12, wrap="word", bg=WASH, relief="flat")
        self.chat_text.pack(fill="both", expand=True)
        self.render_chat()
        row = tk.Frame(chat, bg=PAPER)
        row.pack(fill="x", pady=(6, 0))
        self.chat_entry = ttk.Entry(row)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(row, text="Send", style="Accent.TButton", command=self.send_chat).pack(side="left")

        distractions = self.panel(body, "Distractions", "Distraction Tracker")
        distractions.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.distraction_type_var = tk.StringVar(value="Social media")
        ttk.Combobox(distractions, textvariable=self.distraction_type_var, values=["Social media", "Gaming", "YouTube", "Daydreaming", "Other"], state="readonly").pack(fill="x", pady=3)
        self.distraction_minutes_entry = ttk.Entry(distractions)
        self.distraction_minutes_entry.pack(fill="x", pady=3)
        self.distraction_note_entry = ttk.Entry(distractions)
        self.distraction_note_entry.pack(fill="x", pady=3)
        ttk.Button(distractions, text="Record distraction", style="Accent.TButton", command=self.add_distraction).pack(fill="x", pady=4)
        for item in self.state_data["distractions"][:8]:
            tk.Label(distractions, text=f"{item['date']} · {item['type']} · {item['minutes']}m · {item.get('note', '')}", bg=PAPER, fg=INK, wraplength=430, justify="left").pack(anchor="w", pady=2)

    def render_steps(self):
        if not hasattr(self, "steps_frame"):
            return
        for child in self.steps_frame.winfo_children():
            child.destroy()
        for index, step in enumerate(self.state_data.get("last_breakdown", []), start=1):
            tk.Label(self.steps_frame, text=f"{index}. {step}", bg=PAPER, fg=INK, anchor="w", wraplength=430, justify="left").pack(fill="x", pady=2)

    def build_routines_page(self):
        page = self.pages["routines"]
        page.clear()
        body = page.inner
        body.columnconfigure((0, 1), weight=1, uniform="routines")

        self.build_routine_panel(body, "Morning routine", "morning", 0)
        self.build_routine_panel(body, "Evening routine", "evening", 1)

        journal = self.panel(body, "End of day", "Reflection Journal")
        journal.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        entry = self.state_data["journal"].get(today_key(), {})
        self.journal_well = self.text_field(journal, "What went well?", entry.get("well", ""))
        self.journal_difficult = self.text_field(journal, "What was difficult?", entry.get("difficult", ""))
        self.journal_tomorrow = self.text_field(journal, "What will I do tomorrow?", entry.get("tomorrow", ""))
        ttk.Button(journal, text="Save reflection", style="Accent.TButton", command=self.save_journal).pack(fill="x", pady=8)

    def build_routine_panel(self, parent, title, key, column):
        panel = self.panel(parent, title, "Routine Builder")
        panel.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)
        row = tk.Frame(panel, bg=PAPER)
        row.pack(fill="x", pady=4)
        entry = ttk.Entry(row)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(row, text="+", style="Accent.TButton", command=lambda: self.add_routine_item(key, entry)).pack(side="left")
        for item in self.state_data["routines"][key]:
            item_row = tk.Frame(panel, bg=WASH, highlightbackground=LINE, highlightthickness=1, padx=8, pady=5)
            item_row.pack(fill="x", pady=3)
            var = tk.BooleanVar(value=item.get("done", False))
            ttk.Checkbutton(item_row, variable=var, command=lambda routine=key, routine_item=item, value=var: self.toggle_routine(routine, routine_item, value)).pack(side="left")
            tk.Label(item_row, text=item["title"], bg=WASH, fg=INK, anchor="w").pack(side="left", fill="x", expand=True)
            ttk.Button(item_row, text="×", width=3, command=lambda routine=key, routine_item=item: self.remove_routine(routine, routine_item)).pack(side="right")

    def text_field(self, parent, label, value):
        tk.Label(parent, text=label, bg=PAPER, fg=INK, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 2))
        text = tk.Text(parent, height=4, wrap="word", bg=WASH, fg=INK, relief="flat", padx=8, pady=6)
        text.insert("1.0", value)
        text.pack(fill="x")
        return text

    def build_reports_page(self):
        page = self.pages["reports"]
        page.clear()
        body = page.inner
        body.columnconfigure((0, 1), weight=1, uniform="reports")

        review = self.panel(body, "This week", "AI Weekly Review")
        review.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.weekly_text = tk.Text(review, height=14, wrap="word", bg="#EAF8FC", fg=INK, relief="flat", padx=10, pady=8)
        self.weekly_text.pack(fill="both", expand=True)
        self.render_weekly_review()
        ttk.Button(review, text="Refresh", style="Soft.TButton", command=self.render_weekly_review).pack(fill="x", pady=6)

        partner = self.panel(body, "Progress sharing", "Accountability Partner Mode")
        partner.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.partner_name_entry = ttk.Entry(partner)
        self.partner_name_entry.insert(0, self.state_data["partner"].get("name", ""))
        self.partner_name_entry.pack(fill="x", pady=4)
        self.partner_email_entry = ttk.Entry(partner)
        self.partner_email_entry.insert(0, self.state_data["partner"].get("email", ""))
        self.partner_email_entry.pack(fill="x", pady=4)
        ttk.Button(partner, text="Save partner", style="Accent.TButton", command=self.save_partner).pack(fill="x", pady=4)
        ttk.Button(partner, text="Copy weekly report", style="Soft.TButton", command=self.copy_weekly_report).pack(fill="x", pady=4)
        ttk.Button(partner, text="Export PDF report", style="Accent.TButton", command=self.export_pdf_report).pack(fill="x", pady=4)

    def build_settings_page(self):
        page = self.pages["settings"]
        page.clear()
        body = page.inner
        panel = self.panel(body, "Sensory settings", "Especially helpful for low-overload work")
        panel.pack(fill="x", padx=8, pady=8)
        settings = self.state_data["settings"]
        self.setting_vars = {}
        for key, label in [
            ("reduce_animations", "Reduce animations"),
            ("dark_mode", "Dark mode"),
            ("low_stimulation", "Low stimulation mode"),
            ("high_contrast", "High contrast mode"),
            ("sound", "Sound on/off"),
        ]:
            var = tk.BooleanVar(value=settings.get(key, False))
            self.setting_vars[key] = var
            ttk.Checkbutton(panel, text=label, variable=var, command=self.save_settings).pack(anchor="w", pady=5)
        tk.Label(panel, text="This Python version keeps the interface readable by default. The logo colours are used for emphasis, and sound is optional.", bg=PAPER, fg=MUTED, wraplength=700, justify="left").pack(anchor="w", pady=(12, 0))

    def draw_timer(self):
        if not hasattr(self, "timer_canvas"):
            return
        timer = self.state_data["timer"]
        canvas = self.timer_canvas
        canvas.delete("all")
        size = 230
        x = y = 15
        seconds_left = max(0, int(timer["seconds_left"]))
        total = max(1, int(timer["total_seconds"]))
        progress = 1 - seconds_left / total
        canvas.create_oval(x, y, x + size, y + size, outline=LINE, width=22)
        canvas.create_arc(x, y, x + size, y + size, start=90, extent=-360 * progress, style="arc", outline=CYAN, width=22)
        canvas.create_arc(x, y, x + size, y + size, start=90 - 360 * progress, extent=-12, style="arc", outline=LIME, width=22)
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        canvas.create_text(130, 118, text=f"{minutes:02}:{seconds:02}", fill=INK, font=("Segoe UI Black", 34))
        canvas.create_text(130, 157, text=timer["phase"], fill=MUTED, font=("Segoe UI", 11))

    def start_timer(self):
        self.apply_custom_timer(silent=True)
        self.state_data["timer"]["running"] = True
        self.status_var.set("One tiny step is enough to start.")
        self.save_state()

    def pause_timer(self):
        self.state_data["timer"]["running"] = False
        self.status_var.set("Paused. Nothing is lost.")
        self.save_state()

    def reset_timer(self):
        timer = self.state_data["timer"]
        timer["running"] = False
        timer["phase"] = "Focus"
        timer["seconds_left"] = int(timer["focus_minutes"]) * 60
        timer["total_seconds"] = timer["seconds_left"]
        self.status_var.set("Would now be a good time to begin?")
        self.draw_timer()
        self.save_state()

    def continue_session(self):
        timer = self.state_data["timer"]
        timer["phase"] = "Focus"
        timer["seconds_left"] = int(timer["focus_minutes"]) * 60
        timer["total_seconds"] = timer["seconds_left"]
        timer["running"] = True
        self.add_xp(5)
        self.status_var.set("Continuing gently. You only need the next minute.")
        self.save_state()

    def change_timer_mode(self):
        mode = self.mode_var.get()
        timer = self.state_data["timer"]
        timer["mode"] = mode
        if mode == "25/5":
            timer["focus_minutes"], timer["break_minutes"] = 25, 5
        elif mode == "50/10":
            timer["focus_minutes"], timer["break_minutes"] = 50, 10
        else:
            timer["focus_minutes"] = int(self.custom_focus.get())
            timer["break_minutes"] = int(self.custom_break.get())
        self.reset_timer()

    def apply_custom_timer(self, silent=False):
        timer = self.state_data["timer"]
        if self.mode_var.get() == "Custom":
            timer["mode"] = "Custom"
            timer["focus_minutes"] = max(5, min(180, int(self.custom_focus.get())))
            timer["break_minutes"] = max(1, min(60, int(self.custom_break.get())))
            if not timer["running"]:
                timer["seconds_left"] = timer["focus_minutes"] * 60
                timer["total_seconds"] = timer["seconds_left"]
        if not silent:
            self.status_var.set("Custom timer applied.")
        self.draw_timer()
        self.save_state()

    def update_timer_task(self):
        self.state_data["timer"]["task"] = self.task_var.get() or "Focus session"
        self.save_state()

    def tick_timer(self):
        timer = self.state_data["timer"]
        if timer.get("running"):
            timer["seconds_left"] -= 1
            if timer["seconds_left"] <= 0:
                self.complete_timer_phase()
            self.draw_timer()
            self.save_state()
        self.after(1000, self.tick_timer)

    def complete_timer_phase(self):
        timer = self.state_data["timer"]
        timer["running"] = False
        if timer["phase"] == "Focus":
            self.add_study_minutes(timer["focus_minutes"], "Focus")
            self.add_xp(timer["focus_minutes"])
            timer["phase"] = "Break"
            timer["seconds_left"] = timer["break_minutes"] * 60
            timer["total_seconds"] = timer["seconds_left"]
            self.notify("Focus session complete. Take the break you planned.")
        else:
            timer["phase"] = "Focus"
            timer["seconds_left"] = timer["focus_minutes"] * 60
            timer["total_seconds"] = timer["seconds_left"]
            self.notify("Break complete. Would now be a good time to continue?")
        self.refresh_all()

    def emergency_focus(self):
        self.notebook.select(self.pages["today"])
        self.start_timer()
        messagebox.showinfo("Emergency Focus", f"Only this task matters now:\n\n{self.task_var.get()}\n\nThe timer has started.")

    def add_task(self):
        title = self.task_title_entry.get().strip()
        if not title:
            return
        self.state_data["tasks"].insert(0, {
            "id": new_id(),
            "title": title,
            "priority": self.task_priority_var.get(),
            "subject": self.task_subject_entry.get().strip() or "General",
            "done": False,
            "created": today_key(),
        })
        self.add_xp(2)
        self.refresh_all()

    def toggle_task(self, task, var):
        task["done"] = bool(var.get())
        if task["done"]:
            self.add_xp(8)
        self.refresh_all()

    def remove_task(self, task):
        self.state_data["tasks"] = [item for item in self.state_data["tasks"] if item["id"] != task["id"]]
        self.refresh_all()

    def add_study_log(self):
        try:
            minutes = int(self.study_minutes_entry.get())
        except ValueError:
            messagebox.showwarning("Study time", "Please enter minutes as a number.")
            return
        self.add_study_minutes(minutes, self.study_subject_entry.get().strip() or "Study", self.target_start_entry.get().strip(), self.target_end_entry.get().strip())
        self.add_xp(max(1, minutes // 2))
        self.refresh_all()

    def add_study_minutes(self, minutes, subject, target_start="", target_end=""):
        self.state_data["study_logs"].insert(0, {
            "id": new_id(),
            "date": today_key(),
            "minutes": int(minutes),
            "subject": subject,
            "target_start": target_start,
            "target_end": target_end,
        })

    def save_checkin(self):
        self.state_data["checkins"][today_key()] = {
            "mood": self.mood_var.get(),
            "energy": self.energy_var.get(),
            "stress": self.stress_var.get(),
        }
        self.add_xp(5)
        self.notify("Check-in saved. Thank you for noticing where you are today.")
        self.refresh_all()

    def today_checkin(self):
        return self.state_data.get("checkins", {}).get(today_key(), {})

    def add_reminder(self):
        time_text = self.reminder_time_entry.get().strip()
        text = self.reminder_text_entry.get().strip()
        if not time_text or not text:
            return
        self.state_data["reminders"].append({"id": new_id(), "time": time_text, "text": text, "fired_on": ""})
        self.refresh_all()

    def check_reminders(self):
        now = datetime.now().strftime("%H:%M")
        for reminder in self.state_data["reminders"]:
            if reminder["time"] == now and reminder.get("fired_on") != today_key():
                reminder["fired_on"] = today_key()
                self.notify(reminder["text"])
        self.save_state()
        self.after(30000, self.check_reminders)

    def add_time_block(self):
        self.state_data["planner_blocks"].append({
            "id": new_id(),
            "date": today_key(),
            "hour": int(self.hour_var.get()),
            "type": self.selected_block_var.get(),
        })
        self.refresh_all()

    def remove_block(self, block):
        self.state_data["planner_blocks"] = [item for item in self.state_data["planner_blocks"] if item["id"] != block["id"]]
        self.refresh_all()

    def add_deadline(self):
        title = self.deadline_title_entry.get().strip()
        deadline_date = self.deadline_date_entry.get().strip()
        if not title:
            return
        try:
            parse_day(deadline_date)
        except ValueError:
            messagebox.showwarning("Deadline", "Please use YYYY-MM-DD for the date.")
            return
        self.state_data["deadlines"].append({"id": new_id(), "title": title, "date": deadline_date, "type": self.deadline_type_var.get()})
        self.refresh_all()

    def break_task_down(self):
        task = self.breakdown_entry.get().strip()
        if not task:
            return
        lower = task.lower()
        if "essay" in lower:
            steps = ["Open document", "Create title", "Research sources", "Write introduction", "Write first section", "Save and choose the next section"]
        elif "exam" in lower or "test" in lower:
            steps = ["List topics", "Mark the hardest topic", "Review notes for 10 minutes", "Do three practice questions", "Write one question for a teacher or friend"]
        elif "clean" in lower or "room" in lower:
            steps = ["Choose one small area", "Set a 10 minute timer", "Put rubbish in one bag", "Move dishes or laundry", "Stop when the timer ends"]
        else:
            steps = [f"Name the smallest visible part of '{task}'", "Open the tool or material", "Set a 10 minute timer", "Do one tiny chunk", "Write the next action before stopping"]
        self.state_data["last_breakdown"] = steps
        self.refresh_all()

    def add_steps_to_tasks(self):
        for step in self.state_data.get("last_breakdown", []):
            self.state_data["tasks"].append({"id": new_id(), "title": step, "priority": "Important", "subject": "Breakdown", "done": False, "created": today_key()})
        self.add_xp(len(self.state_data.get("last_breakdown", [])))
        self.notify("Steps added to the to-do list.")
        self.refresh_all()

    def suggest_goals(self):
        if not hasattr(self, "goal_text"):
            return
        try:
            minutes = max(10, min(600, int(self.goal_minutes_entry.get())))
        except ValueError:
            minutes = 240
        minimum = max(10, round(minutes * 0.125 / 5) * 5)
        target = max(minimum + 10, round(minutes * 0.5 / 5) * 5)
        text = (
            f"Minimum Goal: {minimum} min\n"
            "Open the work and complete one small action.\n\n"
            f"Target Goal: {target} min\n"
            "Finish the useful middle version.\n\n"
            f"Stretch Goal: {minutes} min\n"
            "Continue only if energy is still available."
        )
        self.goal_text.delete("1.0", "end")
        self.goal_text.insert("1.0", text)

    def send_chat(self):
        text = self.chat_entry.get().strip()
        if not text:
            return
        self.state_data["chat"].append({"role": "you", "text": text})
        self.state_data["chat"].append({"role": "coach", "text": self.coach_reply(text)})
        self.refresh_all()

    def render_chat(self):
        self.chat_text.delete("1.0", "end")
        for message in self.state_data["chat"][-14:]:
            name = "You" if message["role"] == "you" else "Coach"
            self.chat_text.insert("end", f"{name}: {message['text']}\n\n")
        self.chat_text.configure(state="disabled")

    def coach_reply(self, text):
        lower = text.lower()
        biggest = self.biggest_distraction()
        if "weak" in lower or "improve" in lower:
            weak = f"{biggest[0].lower()} distraction" if biggest else "starting friction"
            return f"Your current weak point looks like {weak}. Try a 10 minute minimum goal, then stop or continue based on energy."
        if "focus" in lower or "adhd" in lower:
            return "Use Emergency Focus, write only the current task, and begin with a timer that feels almost too easy. 10-15 minutes counts."
        if "deadline" in lower or "exam" in lower:
            next_item = self.next_deadline()
            if next_item:
                days = (parse_day(next_item["date"]) - date.today()).days
                return f"{next_item['title']} is {self.days_label(days)}. Put one Study block before the next rest block."
            return "Add the deadline first, then split it into review blocks across the calendar."
        if "burnout" in lower or "tired" in lower:
            return "Treat tiredness as information. Pick the Minimum Goal, lower sensory load, and protect one real rest block."
        return "Choose one task, make it smaller, set a gentle timer, and record what happened afterwards."

    def add_distraction(self):
        try:
            minutes = int(self.distraction_minutes_entry.get())
        except ValueError:
            messagebox.showwarning("Distraction", "Please enter minutes as a number.")
            return
        self.state_data["distractions"].insert(0, {
            "id": new_id(),
            "date": today_key(),
            "type": self.distraction_type_var.get(),
            "minutes": minutes,
            "note": self.distraction_note_entry.get().strip(),
        })
        self.refresh_all()

    def add_routine_item(self, key, entry):
        title = entry.get().strip()
        if not title:
            return
        self.state_data["routines"][key].append({"id": new_id(), "title": title, "done": False})
        self.refresh_all()

    def toggle_routine(self, key, item, var):
        item["done"] = bool(var.get())
        if item["done"]:
            self.add_xp(3)
        self.refresh_all()

    def remove_routine(self, key, item):
        self.state_data["routines"][key] = [candidate for candidate in self.state_data["routines"][key] if candidate["id"] != item["id"]]
        self.refresh_all()

    def save_journal(self):
        self.state_data["journal"][today_key()] = {
            "well": self.journal_well.get("1.0", "end").strip(),
            "difficult": self.journal_difficult.get("1.0", "end").strip(),
            "tomorrow": self.journal_tomorrow.get("1.0", "end").strip(),
        }
        self.add_xp(6)
        self.notify("Reflection saved.")
        self.refresh_all()

    def render_weekly_review(self):
        if not hasattr(self, "weekly_text"):
            return
        best = max(self.daily_totals(7), key=lambda item: item["minutes"])
        biggest = self.biggest_distraction()
        total = self.total_minutes_since(7)
        recommendation = self.weekly_recommendation(total, biggest)
        lines = [
            f"Total study time: {total / 60:.1f}h ({total} minutes)",
            f"Best focus day: {best['date']} with {best['minutes']} minutes" if best["minutes"] else "Best focus day: not enough data yet",
            f"Biggest distraction: {biggest[0]}, {biggest[1]} minutes" if biggest else "Biggest distraction: none recorded",
            f"Mood trend: {self.mood_trend()}",
            f"Recommended improvement: {recommendation}",
        ]
        self.weekly_text.configure(state="normal")
        self.weekly_text.delete("1.0", "end")
        self.weekly_text.insert("1.0", "\n".join(lines))

    def save_partner(self):
        self.state_data["partner"] = {
            "name": self.partner_name_entry.get().strip(),
            "email": self.partner_email_entry.get().strip(),
        }
        self.notify("Accountability partner saved.")
        self.save_state()

    def copy_weekly_report(self):
        text = self.report_text()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.notify("Weekly report copied.")

    def export_pdf_report(self):
        path = filedialog.asksaveasfilename(
            title="Export PDF report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="tijdmanager-progress-report.pdf",
        )
        if not path:
            return
        write_simple_pdf(Path(path), self.report_text().splitlines())
        self.notify("PDF report exported.")

    def report_text(self):
        return (
            "TIJDMANAGER Progress Report\n\n"
            f"This week\n{self.weekly_text.get('1.0', 'end').strip() if hasattr(self, 'weekly_text') else ''}\n\n"
            f"Completion rate: {self.completion_rate()}%\n"
            f"Focus score: {self.focus_score()}\n"
            f"Streak: {self.streak()} days\n"
        )

    def save_settings(self):
        for key, var in self.setting_vars.items():
            self.state_data["settings"][key] = bool(var.get())
        self.save_state()
        self.notify("Sensory settings saved.")

    def update_language(self):
        self.state_data["settings"]["language"] = self.language_var.get()
        self.save_state()
        self.notify(f"Language preference saved: {self.language_var.get()}")

    def add_xp(self, amount):
        self.state_data["xp"] = max(0, int(self.state_data.get("xp", 0)) + int(amount))

    def notify(self, text):
        self.status_var.set(text)
        if self.state_data["settings"].get("sound"):
            self.bell()

    def daily_totals(self, days):
        result = []
        for offset in range(days):
            key = day_key(-offset)
            result.append({"date": key, "minutes": self.total_minutes_for_date(key)})
        return result

    def total_minutes_for_date(self, key):
        return sum(int(item["minutes"]) for item in self.state_data["study_logs"] if item["date"] == key)

    def total_minutes_since(self, days):
        return sum(item["minutes"] for item in self.daily_totals(days))

    def completion_rate(self):
        tasks = self.state_data["tasks"]
        if not tasks:
            return 0
        return round(sum(1 for item in tasks if item.get("done")) / len(tasks) * 100)

    def focus_score(self):
        study = self.total_minutes_since(7)
        distractions = sum(int(item["minutes"]) for item in self.state_data["distractions"] if parse_day(item["date"]) >= date.today() - timedelta(days=7))
        return max(0, min(100, round(study / max(60, study + distractions) * 100)))

    def streak(self):
        count = 0
        for offset in range(365):
            if self.total_minutes_for_date(day_key(-offset)) > 0:
                count += 1
            else:
                break
        return count

    def biggest_distraction(self):
        totals = Counter()
        for item in self.state_data["distractions"]:
            totals[item["type"]] += int(item["minutes"])
        return totals.most_common(1)[0] if totals else None

    def next_deadline(self):
        future = [item for item in self.state_data["deadlines"] if item["date"] >= today_key()]
        return sorted(future, key=lambda item: item["date"])[0] if future else None

    def target_time_summary(self):
        study_hours = sorted(item["hour"] for item in self.state_data["planner_blocks"] if item["date"] == today_key() and item["type"] == "Study")
        if not study_hours:
            return "No study block yet"
        return f"{study_hours[0]:02}:00-{study_hours[-1] + 1:02}:00"

    def days_label(self, days):
        if days < 0:
            return f"{abs(days)} days overdue"
        if days == 0:
            return "Today"
        if days == 1:
            return "Tomorrow"
        return f"{days} days remaining"

    def schedule_suggestion(self, days):
        if days <= 1:
            return "Do a 15 min triage"
        if days <= 3:
            return "Plan 2 short blocks"
        if days <= 7:
            return "Review every other day"
        return "Spread into weekly blocks"

    def insight_text(self):
        biggest = self.biggest_distraction()
        urgent_open = sum(1 for task in self.state_data["tasks"] if task["priority"] == "Urgent" and not task["done"])
        today_minutes = self.total_minutes_for_date(today_key())
        if biggest and biggest[1] >= 20:
            return f"Weak point: {biggest[0].lower()} drift.\nNext step: place a Break block before the next Study block, then start Emergency Focus."
        if urgent_open >= 2:
            return "Weak point: urgent task overload.\nNext step: turn the top urgent task into three smaller steps."
        if today_minutes == 0:
            return "Weak point: the first start of the day.\nNext step: use the Minimum Goal: 10-15 minutes only."
        return "Weak point: keeping momentum visible.\nNext step: record the next small study block after you finish."

    def burnout_text(self):
        last_three = sum(item["minutes"] for item in self.daily_totals(3))
        previous_three = sum(self.total_minutes_for_date(day_key(-offset)) for offset in range(3, 6))
        today = self.today_checkin()
        skipped = sum(1 for item in self.state_data["tasks"] if not item.get("done"))
        risk = 0
        if previous_three > 0 and last_three < previous_three * 0.55:
            risk += 1
        if today.get("mood") == "Difficult" or today.get("stress", 0) >= 8:
            risk += 1
        if skipped >= 5:
            risk += 1
        if risk >= 2:
            return "Burnout risk: rising.\nLower today's target, add rest, and keep only one urgent next action."
        if risk == 1:
            return "Burnout signal: watch gently.\nUse a minimum goal and avoid catching up all at once."
        return "Burnout risk: low.\nKeep rest visible in the plan so progress stays sustainable."

    def mood_trend(self):
        scores = {"Difficult": 1, "Okay": 2, "Good": 3, "Great": 4}
        entries = sorted(self.state_data["checkins"].items())[-7:]
        if len(entries) < 2:
            return "not enough check-ins yet"
        values = [scores.get(value.get("mood"), 2) for _, value in entries]
        if values[-1] > values[0]:
            return "improving"
        if values[-1] < values[0]:
            return "getting heavier"
        return "steady"

    def weekly_recommendation(self, total, biggest):
        if total < 120:
            return "use Minimum Goals for four days before increasing target time."
        if biggest and biggest[1] > 30:
            return f"protect breaks from {biggest[0].lower()} with a clear end point."
        if self.completion_rate() < 55:
            return "split urgent tasks into smaller steps before starting the timer."
        return "keep the same rhythm and add one planned rest block."

    def on_close(self):
        self.save_state()
        self.destroy()


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(path: Path, lines: list[str]):
    wrapped = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=88) or [""])
    wrapped = wrapped[:48]
    content_lines = ["BT", "/F1 12 Tf", "14 TL", "50 792 Td"]
    for line in wrapped:
        content_lines.append(f"({escape_pdf_text(line)}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"
    xref_at = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii")
    path.write_bytes(pdf)


if __name__ == "__main__":
    app = TijdmanagerApp()
    app.mainloop()
