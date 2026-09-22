import base64
import hashlib
import hmac
import json
import random
import re
import secrets
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, scrolledtext


APP_NAME = "SÕBRAD"
DATA_FILE = Path(__file__).with_name("sobrad_data.json")

TITLE = "#00A3E0"
BACKGROUND = "#FFFFFF"
OPTION_BUTTON = "#DDEB47"
NAVY = "#0E3A5F"
TEXT = "#173047"
MUTED = "#62798B"
LINE = "#DCEAF0"
SOFT = "#F5FBFD"
DANGER = "#B93645"

SUBTITLES = [
    "If you've experienced bullying, violence, or trauma, or you just don't have anyone to talk to right now, I'm here.",
    "For anyone carrying something heavy. Talk to me.",
    "Feeling overwhelmed, panicked, or alone? Let's get through this moment together.",
]

CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bend my life\b",
    r"\bi want to die\b",
    r"\bwant to die\b",
    r"\bcan't go on\b",
    r"\bcannot go on\b",
    r"\bno reason to live\b",
    r"\bhurt myself\b",
    r"\bself[-\s]?harm\b",
    r"\boverdose\b",
    r"\bhang myself\b",
    r"\bjump off\b",
]

HOME_OPTIONS = [
    ("mood", "home_mood"),
    ("chat", "home_chat"),
    ("emergency", "home_emergency"),
    ("journal", "home_journal"),
    ("exercises", "home_exercises"),
    ("goals", "home_goals"),
    ("dashboard", "home_dashboard"),
    ("privacy", "home_privacy"),
]

LANGUAGES = [
    ("en", "🇬🇧 English (UK)"),
    ("fr", "🇫🇷 Français"),
    ("nl", "🇳🇱 Nederlands"),
    ("et", "🇪🇪 Eesti"),
    ("es", "🇪🇸 Español"),
    ("it", "🇮🇹 Italiano"),
    ("pt", "🇵🇹 Portuguese"),
    ("de", "🇩🇪 Deutsch"),
    ("fi", "🇫🇮 Suomi"),
    ("sv", "🇸🇪 Svenska"),
    ("ja", "🇯🇵 日本語"),
]

LANGUAGE_LABELS = {code: label for code, label in LANGUAGES}
LANGUAGE_CODES = {label: code for code, label in LANGUAGES}

TRANSLATIONS = {
    "en": {
        "language": "Language",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm password",
        "login": "Log in",
        "create_account": "Create account",
        "anonymous_mode": "Anonymous mode",
        "home": "Home",
        "home_mood": "Mood Check-In",
        "home_chat": "Talk to AI Companion",
        "home_emergency": "Emergency Help",
        "home_journal": "Journal",
        "home_exercises": "Recovery Exercises",
        "home_goals": "Goals and Future Planning",
        "home_dashboard": "Progress Dashboard",
        "home_privacy": "Privacy and Security",
        "today": "Today",
        "home_title": "A quieter place to begin again.",
        "home_hint": "Choose the smallest useful next step.",
        "home_hint_new": "This can be a steady place for the next minute.",
        "companion": "Companion",
        "talk_title": "Talk with SÕBRAD",
        "settings": "Settings",
        "privacy_title": "Privacy and access",
        "save_language": "Language changes save automatically.",
    },
    "fr": {
        "language": "Langue", "username": "Nom d'utilisateur", "password": "Mot de passe",
        "confirm_password": "Confirmer le mot de passe", "login": "Connexion", "create_account": "Créer un compte",
        "anonymous_mode": "Mode anonyme", "home": "Accueil", "home_mood": "Humeur", "home_chat": "Parler au compagnon IA",
        "home_emergency": "Aide d'urgence", "home_journal": "Journal", "home_exercises": "Exercices de récupération",
        "home_goals": "Objectifs et avenir", "home_dashboard": "Tableau de progrès", "home_privacy": "Confidentialité",
        "today": "Aujourd'hui", "home_title": "Un endroit plus calme pour recommencer.", "companion": "Compagnon",
        "talk_title": "Parler avec SÕBRAD", "settings": "Réglages", "privacy_title": "Confidentialité et accès",
    },
    "nl": {
        "language": "Taal", "username": "Gebruikersnaam", "password": "Wachtwoord",
        "confirm_password": "Bevestig wachtwoord", "login": "Inloggen", "create_account": "Account maken",
        "anonymous_mode": "Anonieme modus", "home": "Start", "home_mood": "Stemming", "home_chat": "Praat met AI-maatje",
        "home_emergency": "Noodhulp", "home_journal": "Dagboek", "home_exercises": "Hersteloefeningen",
        "home_goals": "Doelen en toekomst", "home_dashboard": "Voortgang", "home_privacy": "Privacy",
        "today": "Vandaag", "home_title": "Een stillere plek om opnieuw te beginnen.", "companion": "Maatje",
        "talk_title": "Praat met SÕBRAD", "settings": "Instellingen", "privacy_title": "Privacy en toegang",
    },
    "et": {
        "language": "Keel", "username": "Kasutajanimi", "password": "Parool",
        "confirm_password": "Kinnita parool", "login": "Logi sisse", "create_account": "Loo konto",
        "anonymous_mode": "Anonüümne režiim", "home": "Avaleht", "home_mood": "Meeleolu", "home_chat": "Räägi AI-kaaslasega",
        "home_emergency": "Hädaabi", "home_journal": "Päevik", "home_exercises": "Taastumise harjutused",
        "home_goals": "Eesmärgid ja tulevik", "home_dashboard": "Edusammud", "home_privacy": "Privaatsus",
        "today": "Täna", "home_title": "Rahulikum koht, kust uuesti alustada.", "companion": "Kaaslane",
        "talk_title": "Räägi SÕBRADiga", "settings": "Seaded", "privacy_title": "Privaatsus ja ligipääs",
    },
    "es": {
        "language": "Idioma", "username": "Usuario", "password": "Contraseña",
        "confirm_password": "Confirmar contraseña", "login": "Entrar", "create_account": "Crear cuenta",
        "anonymous_mode": "Modo anónimo", "home": "Inicio", "home_mood": "Estado de ánimo", "home_chat": "Hablar con IA",
        "home_emergency": "Ayuda de emergencia", "home_journal": "Diario", "home_exercises": "Ejercicios de recuperación",
        "home_goals": "Metas y futuro", "home_dashboard": "Progreso", "home_privacy": "Privacidad",
        "today": "Hoy", "home_title": "Un lugar más tranquilo para empezar otra vez.", "companion": "Compañía",
        "talk_title": "Habla con SÕBRAD", "settings": "Ajustes", "privacy_title": "Privacidad y acceso",
    },
    "it": {
        "language": "Lingua", "username": "Nome utente", "password": "Password",
        "confirm_password": "Conferma password", "login": "Accedi", "create_account": "Crea account",
        "anonymous_mode": "Modalità anonima", "home": "Home", "home_mood": "Umore", "home_chat": "Parla con IA",
        "home_emergency": "Aiuto d'emergenza", "home_journal": "Diario", "home_exercises": "Esercizi di recupero",
        "home_goals": "Obiettivi e futuro", "home_dashboard": "Progresso", "home_privacy": "Privacy",
        "today": "Oggi", "home_title": "Un posto più quieto per ricominciare.", "companion": "Compagno",
        "talk_title": "Parla con SÕBRAD", "settings": "Impostazioni", "privacy_title": "Privacy e accesso",
    },
    "pt": {
        "language": "Idioma", "username": "Nome de utilizador", "password": "Palavra-passe",
        "confirm_password": "Confirmar palavra-passe", "login": "Entrar", "create_account": "Criar conta",
        "anonymous_mode": "Modo anónimo", "home": "Início", "home_mood": "Humor", "home_chat": "Falar com IA",
        "home_emergency": "Ajuda de emergência", "home_journal": "Diário", "home_exercises": "Exercícios de recuperação",
        "home_goals": "Metas e futuro", "home_dashboard": "Progresso", "home_privacy": "Privacidade",
        "today": "Hoje", "home_title": "Um lugar mais calmo para recomeçar.", "companion": "Companhia",
        "talk_title": "Fale com SÕBRAD", "settings": "Definições", "privacy_title": "Privacidade e acesso",
    },
    "de": {
        "language": "Sprache", "username": "Benutzername", "password": "Passwort",
        "confirm_password": "Passwort bestätigen", "login": "Anmelden", "create_account": "Konto erstellen",
        "anonymous_mode": "Anonymer Modus", "home": "Start", "home_mood": "Stimmung", "home_chat": "Mit KI sprechen",
        "home_emergency": "Notfallhilfe", "home_journal": "Journal", "home_exercises": "Übungen zur Stabilisierung",
        "home_goals": "Ziele und Zukunft", "home_dashboard": "Fortschritt", "home_privacy": "Privatsphäre",
        "today": "Heute", "home_title": "Ein ruhigerer Ort für einen neuen Anfang.", "companion": "Begleitung",
        "talk_title": "Mit SÕBRAD sprechen", "settings": "Einstellungen", "privacy_title": "Privatsphäre und Zugang",
    },
    "fi": {
        "language": "Kieli", "username": "Käyttäjänimi", "password": "Salasana",
        "confirm_password": "Vahvista salasana", "login": "Kirjaudu", "create_account": "Luo tili",
        "anonymous_mode": "Anonyymi tila", "home": "Koti", "home_mood": "Mieli", "home_chat": "Puhu AI-kumppanille",
        "home_emergency": "Hätäapu", "home_journal": "Päiväkirja", "home_exercises": "Toipumisharjoitukset",
        "home_goals": "Tavoitteet ja tulevaisuus", "home_dashboard": "Edistyminen", "home_privacy": "Yksityisyys",
        "today": "Tänään", "home_title": "Rauhallisempi paikka aloittaa uudelleen.", "companion": "Kumppani",
        "talk_title": "Puhu SÕBRADille", "settings": "Asetukset", "privacy_title": "Yksityisyys ja pääsy",
    },
    "sv": {
        "language": "Språk", "username": "Användarnamn", "password": "Lösenord",
        "confirm_password": "Bekräfta lösenord", "login": "Logga in", "create_account": "Skapa konto",
        "anonymous_mode": "Anonymt läge", "home": "Hem", "home_mood": "Mående", "home_chat": "Prata med AI",
        "home_emergency": "Akut hjälp", "home_journal": "Journal", "home_exercises": "Återhämtningsövningar",
        "home_goals": "Mål och framtid", "home_dashboard": "Framsteg", "home_privacy": "Integritet",
        "today": "Idag", "home_title": "En lugnare plats att börja om.", "companion": "Följeslagare",
        "talk_title": "Prata med SÕBRAD", "settings": "Inställningar", "privacy_title": "Integritet och åtkomst",
    },
    "ja": {
        "language": "言語", "username": "ユーザー名", "password": "パスワード",
        "confirm_password": "パスワード確認", "login": "ログイン", "create_account": "アカウント作成",
        "anonymous_mode": "匿名モード", "home": "ホーム", "home_mood": "気分チェック", "home_chat": "AIコンパニオンと話す",
        "home_emergency": "緊急ヘルプ", "home_journal": "日記", "home_exercises": "回復エクササイズ",
        "home_goals": "目標と未来", "home_dashboard": "進捗", "home_privacy": "プライバシー",
        "today": "今日", "home_title": "もう一度始めるための静かな場所。", "companion": "コンパニオン",
        "talk_title": "SÕBRAD と話す", "settings": "設定", "privacy_title": "プライバシーとアクセス",
    },
}

GROUNDING_PROMPTS = [
    "Name five things you can see. Let your eyes move slowly.",
    "Name four things you can feel. Notice texture, pressure, and temperature.",
    "Name three things you can hear. Let the sounds arrive without chasing them.",
    "Name two things you can smell. If nothing is there, choose two scents you like.",
    "Name one thing you can taste. Then take one slower breath.",
]


def default_state():
    return {
        "accepted_disclaimer": False,
        "language": "en",
        "user": None,
        "anonymous": False,
        "moods": [],
        "chat": [],
        "journal": [],
        "goals": [],
        "completed_goals": 0,
        "triggers": [],
        "safety": {"trusted": "", "place": "", "action": ""},
        "skills": {"breathing": 0, "grounding": 0},
    }


def load_state():
    if not DATA_FILE.exists():
        return default_state()
    try:
        loaded = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        state = default_state()
        state.update(loaded)
        return state
    except Exception:
        return default_state()


def save_state(state):
    DATA_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def password_hash(username, password):
    return hashlib.sha256(f"{username}:{password}".encode("utf-8")).hexdigest()


def b64(data):
    return base64.b64encode(data).decode("ascii")


def from_b64(data):
    return base64.b64decode(data.encode("ascii"))


def derive_key(pin, salt):
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 210_000, dklen=32)


def stream_bytes(key, nonce, length):
    chunks = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < length:
        counter_bytes = counter.to_bytes(8, "big")
        chunks.append(hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest())
        counter += 1
    return b"".join(chunks)[:length]


def encrypt_note(pin, text):
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    key = derive_key(pin, salt)
    plain = text.encode("utf-8")
    mask = stream_bytes(key, nonce, len(plain))
    cipher = bytes(a ^ b for a, b in zip(plain, mask))
    tag = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
    return {"salt": b64(salt), "nonce": b64(nonce), "data": b64(cipher), "tag": b64(tag)}


def decrypt_note(pin, entry):
    salt = from_b64(entry["salt"])
    nonce = from_b64(entry["nonce"])
    cipher = from_b64(entry["data"])
    tag = from_b64(entry["tag"])
    key = derive_key(pin, salt)
    expected = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        raise ValueError("Wrong PIN or damaged journal entry.")
    mask = stream_bytes(key, nonce, len(cipher))
    plain = bytes(a ^ b for a, b in zip(cipher, mask))
    return plain.decode("utf-8")


class CircleOption(tk.Canvas):
    def __init__(self, parent, text, command):
        super().__init__(
            parent,
            width=160,
            height=160,
            bg=BACKGROUND,
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.create_oval(8, 8, 152, 152, fill=OPTION_BUTTON, outline=NAVY, width=2)
        self.create_text(
            80,
            80,
            text=text,
            fill=NAVY,
            font=("Google Sans", 11, "bold"),
            width=118,
            justify="center",
        )
        self.bind("<Button-1>", lambda event: self.command())
        self.bind("<Enter>", lambda event: self.configure(bg=SOFT))
        self.bind("<Leave>", lambda event: self.configure(bg=BACKGROUND))


class SobradApp:
    def __init__(self, root):
        self.root = root
        self.state = load_state()
        self.content = None
        self.breathing = False
        self.breath_phase = 0
        self.grounding_index = 0
        self.root.title(APP_NAME)
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.root.configure(bg=BACKGROUND)
        self.show_login()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def tr(self, key):
        language = self.state.get("language", "en")
        return TRANSLATIONS.get(language, {}).get(key, TRANSLATIONS["en"].get(key, key))

    def language_display(self):
        return LANGUAGE_LABELS.get(self.state.get("language", "en"), LANGUAGE_LABELS["en"])

    def set_language_from_label(self, label, refresh=None):
        self.state["language"] = LANGUAGE_CODES.get(label, "en")
        save_state(self.state)
        if refresh == "login":
            self.show_login()
        elif refresh:
            self.show_shell(refresh)

    def language_selector(self, parent, refresh=None):
        frame = tk.Frame(parent, bg=parent["bg"])
        tk.Label(frame, text=self.tr("language"), fg=NAVY, bg=parent["bg"], font=("Google Sans", 10, "bold")).pack(side="left", padx=(0, 8))
        value = tk.StringVar(value=self.language_display())
        menu = tk.OptionMenu(frame, value, *[label for _, label in LANGUAGES], command=lambda label: self.set_language_from_label(label, refresh))
        menu.configure(bg=BACKGROUND, fg=NAVY, activebackground=SOFT, relief="flat", highlightbackground=LINE)
        menu["menu"].configure(bg=BACKGROUND, fg=NAVY)
        menu.pack(side="left")
        return frame

    def label(self, parent, text, size=12, color=TEXT, bold=False, **grid):
        font = ("Google Sans", size, "bold" if bold else "normal")
        widget = tk.Label(parent, text=text, fg=color, bg=parent["bg"], font=font, wraplength=760, justify="left")
        widget.grid(**grid)
        return widget

    def button(self, parent, text, command, bg=TITLE, fg="white"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            padx=16,
            pady=10,
            bd=0,
            font=("Google Sans", 10, "bold"),
            cursor="hand2",
        )

    def show_login(self):
        self.clear()
        self.root.configure(bg=BACKGROUND)

        outer = tk.Frame(self.root, bg=BACKGROUND, padx=42, pady=42)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)

        left = tk.Frame(outer, bg=BACKGROUND)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        tk.Label(left, text="G'day... Tsau...", fg=NAVY, bg=BACKGROUND, font=("Inter", 12, "bold")).pack(anchor="w")
        tk.Label(left, text=APP_NAME, fg=TITLE, bg=BACKGROUND, font=("Avenir Next", 54, "bold")).pack(anchor="w", pady=(8, 12))
        tk.Label(
            left,
            text=random.choice(SUBTITLES),
            fg=MUTED,
            bg=BACKGROUND,
            font=("Inter", 14),
            wraplength=520,
            justify="left",
        ).pack(anchor="w")

        form = tk.Frame(outer, bg=SOFT, padx=24, pady=24, highlightbackground=LINE, highlightthickness=1)
        form.grid(row=0, column=1, sticky="nsew")
        form.columnconfigure(0, weight=1)

        tk.Label(form, text=self.tr("username"), fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).grid(row=0, column=0, sticky="w")
        username = tk.Entry(form, font=("Google Sans", 12), relief="flat", highlightbackground=LINE, highlightthickness=1)
        username.grid(row=1, column=0, sticky="ew", pady=(6, 16), ipady=8)

        tk.Label(form, text=self.tr("password"), fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).grid(row=2, column=0, sticky="w")
        password = tk.Entry(form, show="*", font=("Google Sans", 12), relief="flat", highlightbackground=LINE, highlightthickness=1)
        password.grid(row=3, column=0, sticky="ew", pady=(6, 18), ipady=8)

        def login():
            name = username.get().strip()
            pwd = password.get()
            if not name or not pwd:
                messagebox.showwarning(APP_NAME, "Enter a username and password.")
                return
            stored = self.state.get("user")
            if not stored:
                messagebox.showinfo(APP_NAME, "No account exists yet. Choose Create account first.")
                return
            pwd_hash = password_hash(name, pwd)
            if stored.get("username") != name:
                messagebox.showerror(APP_NAME, "This local app already has a different username.")
                return
            if stored.get("password_hash") != pwd_hash:
                messagebox.showerror(APP_NAME, "That password does not match this local profile.")
                return
            self.state["anonymous"] = False
            save_state(self.state)
            self.show_shell("home")

        def anonymous():
            self.state["anonymous"] = True
            save_state(self.state)
            self.show_shell("home")

        self.button(form, self.tr("login"), login).grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.button(form, self.tr("create_account"), self.show_create_account, bg=OPTION_BUTTON, fg=NAVY).grid(row=5, column=0, sticky="ew", pady=(0, 10))
        self.button(form, self.tr("anonymous_mode"), anonymous, bg=OPTION_BUTTON, fg=NAVY).grid(row=6, column=0, sticky="ew")
        self.language_selector(form, refresh="login").grid(row=7, column=0, sticky="w", pady=(18, 0))

    def show_create_account(self):
        if self.state.get("user"):
            messagebox.showinfo(APP_NAME, "A local account already exists. Use Privacy to delete all data before creating a new one.")
            return
        modal = tk.Toplevel(self.root)
        modal.title(self.tr("create_account"))
        modal.configure(bg=BACKGROUND)
        modal.transient(self.root)
        modal.grab_set()
        modal.geometry("460x360")
        modal.columnconfigure(0, weight=1)
        tk.Label(modal, text=self.tr("create_account"), fg=TITLE, bg=BACKGROUND, font=("Avenir Next", 24, "bold")).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 14))

        fields = tk.Frame(modal, bg=BACKGROUND, padx=24)
        fields.grid(row=1, column=0, sticky="ew")
        fields.columnconfigure(0, weight=1)
        tk.Label(fields, text=self.tr("username"), fg=NAVY, bg=BACKGROUND, font=("Google Sans", 11, "bold")).grid(row=0, column=0, sticky="w")
        username = tk.Entry(fields, font=("Google Sans", 12), relief="flat", highlightbackground=LINE, highlightthickness=1)
        username.grid(row=1, column=0, sticky="ew", pady=(6, 14), ipady=7)
        tk.Label(fields, text=self.tr("password"), fg=NAVY, bg=BACKGROUND, font=("Google Sans", 11, "bold")).grid(row=2, column=0, sticky="w")
        password = tk.Entry(fields, show="*", font=("Google Sans", 12), relief="flat", highlightbackground=LINE, highlightthickness=1)
        password.grid(row=3, column=0, sticky="ew", pady=(6, 14), ipady=7)
        tk.Label(fields, text=self.tr("confirm_password"), fg=NAVY, bg=BACKGROUND, font=("Google Sans", 11, "bold")).grid(row=4, column=0, sticky="w")
        confirm = tk.Entry(fields, show="*", font=("Google Sans", 12), relief="flat", highlightbackground=LINE, highlightthickness=1)
        confirm.grid(row=5, column=0, sticky="ew", pady=(6, 18), ipady=7)

        def create():
            name = username.get().strip()
            pwd = password.get()
            confirm_pwd = confirm.get()
            if not name or not pwd:
                messagebox.showwarning(APP_NAME, "Enter a username and password.")
                return
            if len(pwd) < 6:
                messagebox.showwarning(APP_NAME, "Use at least 6 characters for the password.")
                return
            if pwd != confirm_pwd:
                messagebox.showerror(APP_NAME, "The passwords do not match.")
                return
            self.state["user"] = {"username": name, "password_hash": password_hash(name, pwd), "created": time.time()}
            self.state["anonymous"] = False
            save_state(self.state)
            modal.destroy()
            self.show_shell("home")

        self.button(modal, self.tr("create_account"), create).grid(row=2, column=0, sticky="e", padx=24, pady=20)

    def show_disclaimer_if_needed(self):
        if self.state.get("accepted_disclaimer"):
            return
        modal = tk.Toplevel(self.root)
        modal.title("Before you begin")
        modal.configure(bg=BACKGROUND)
        modal.transient(self.root)
        modal.grab_set()
        modal.geometry("520x300")
        tk.Label(modal, text="Before you begin", fg=TITLE, bg=BACKGROUND, font=("Avenir Next", 24, "bold")).pack(anchor="w", padx=24, pady=(24, 8))
        tk.Label(
            modal,
            text=(
                "SÕBRAD is not a replacement for professional medical, psychological, or emergency care. "
                "It can help you slow down, write privately, and choose a next step."
            ),
            fg=TEXT,
            bg=BACKGROUND,
            font=("Google Sans", 12),
            wraplength=460,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 16))
        agreed = tk.BooleanVar(value=False)
        tk.Checkbutton(modal, text="I understand.", variable=agreed, fg=NAVY, bg=BACKGROUND, activebackground=BACKGROUND).pack(anchor="w", padx=24)

        def accept():
            if not agreed.get():
                messagebox.showwarning(APP_NAME, "Please check 'I understand' first.")
                return
            self.state["accepted_disclaimer"] = True
            save_state(self.state)
            modal.destroy()

        self.button(modal, "Continue", accept).pack(anchor="e", padx=24, pady=20)

    def show_shell(self, view):
        self.current_view = view
        self.clear()
        header = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=12, highlightbackground=LINE, highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text=APP_NAME, fg=NAVY, bg=BACKGROUND, font=("Avenir Next", 18, "bold")).pack(side="left", padx=(0, 18))
        self.language_selector(header, refresh=view).pack(side="right")
        for key, label_key in [("home", "home")] + HOME_OPTIONS:
            label = self.tr(label_key)
            tk.Button(
                header,
                text=label.split(" and ")[0],
                command=lambda key=key: self.show_shell(key),
                fg=NAVY,
                bg=BACKGROUND,
                activebackground=SOFT,
                relief="flat",
                padx=8,
                pady=6,
                font=("Google Sans", 9, "bold"),
                cursor="hand2",
            ).pack(side="left")

        self.content = tk.Frame(self.root, bg=BACKGROUND, padx=26, pady=24)
        self.content.pack(fill="both", expand=True)
        getattr(self, f"page_{view}")()
        self.show_disclaimer_if_needed()

    def page_title(self, eyebrow, title, subtitle=None):
        tk.Label(self.content, text=eyebrow.upper(), fg=NAVY, bg=BACKGROUND, font=("Inter", 10, "bold")).pack(anchor="w")
        tk.Label(self.content, text=title, fg=TITLE, bg=BACKGROUND, font=("Avenir Next", 32, "bold")).pack(anchor="w", pady=(4, 8))
        if subtitle:
            tk.Label(self.content, text=subtitle, fg=MUTED, bg=BACKGROUND, font=("Inter", 12), wraplength=860, justify="left").pack(anchor="w", pady=(0, 18))

    def page_home(self):
        name = "Anonymous" if self.state.get("anonymous") else self.state.get("user", {}).get("username", "")
        greeting = self.tr("home_hint") if name else self.tr("home_hint_new")
        self.page_title(self.tr("today"), self.tr("home_title"), greeting)
        grid = tk.Frame(self.content, bg=BACKGROUND)
        grid.pack(fill="both", expand=True, pady=8)
        for index, (key, label_key) in enumerate(HOME_OPTIONS):
            row, col = divmod(index, 4)
            cell = tk.Frame(grid, bg=BACKGROUND, padx=12, pady=12)
            cell.grid(row=row, column=col, sticky="nsew")
            grid.columnconfigure(col, weight=1)
            grid.rowconfigure(row, weight=1)
            CircleOption(cell, self.tr(label_key), lambda key=key: self.show_shell(key)).pack()

    def page_mood(self):
        self.page_title("Check-in", "How is this moment?")
        body = tk.Frame(self.content, bg=BACKGROUND)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Mood level", fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w")
        mood_value = tk.IntVar(value=5)
        tk.Scale(left, from_=1, to=10, orient="horizontal", variable=mood_value, bg=SOFT, fg=NAVY, highlightthickness=0).pack(fill="x")
        tk.Label(left, text="What is present?", fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w", pady=(12, 4))
        words = ["numb", "afraid", "angry", "sad", "tired", "hopeful", "steady", "alone"]
        selected = {word: tk.BooleanVar(value=False) for word in words}
        chips = tk.Frame(left, bg=SOFT)
        chips.pack(anchor="w")
        for word in words:
            tk.Checkbutton(chips, text=word, variable=selected[word], bg=SOFT, fg=NAVY, activebackground=SOFT).pack(side="left", padx=(0, 6))
        tk.Label(left, text="Note", fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w", pady=(12, 4))
        note = tk.Text(left, height=5, wrap="word", relief="flat", highlightbackground=LINE, highlightthickness=1)
        note.pack(fill="x")

        def save_mood():
            self.state["moods"].insert(0, {
                "value": mood_value.get(),
                "words": [word for word in words if selected[word].get()],
                "note": note.get("1.0", "end").strip(),
                "time": time.time(),
            })
            self.state["moods"] = self.state["moods"][:60]
            save_state(self.state)
            self.show_shell("mood")

        self.button(left, "Save check-in", save_mood).pack(anchor="e", pady=12)
        tk.Label(right, text="Recent moods", fg=NAVY, bg=SOFT, font=("Google Sans", 13, "bold")).pack(anchor="w")
        self.draw_mood_chart(right)
        for entry in self.state["moods"][:6]:
            words_text = ", ".join(entry.get("words", []))
            note_text = entry.get("note", "")
            tk.Label(right, text=f"{entry['value']}/10  {words_text}  {note_text}", fg=TEXT, bg=SOFT, wraplength=430, justify="left").pack(anchor="w", pady=3)

    def draw_mood_chart(self, parent):
        canvas = tk.Canvas(parent, width=430, height=170, bg=BACKGROUND, highlightbackground=LINE, highlightthickness=1)
        canvas.pack(fill="x", pady=12)
        moods = list(reversed(self.state["moods"][:12]))
        for i in range(1, 6):
            y = 20 + i * 25
            canvas.create_line(24, y, 400, y, fill=LINE)
        if len(moods) < 2:
            canvas.create_text(210, 85, text="No mood check-ins yet.", fill=MUTED)
            return
        points = []
        for index, item in enumerate(moods):
            x = 28 + index * (360 / max(len(moods) - 1, 1))
            y = 145 - ((item["value"] - 1) / 9) * 120
            points.append((x, y))
        for start, end in zip(points, points[1:]):
            canvas.create_line(*start, *end, fill=TITLE, width=3)
        for x, y in points:
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=TITLE, outline=TITLE)

    def page_chat(self):
        self.page_title(self.tr("companion"), self.tr("talk_title"))
        if not self.state["chat"]:
            self.state["chat"].append({"role": "bot", "text": "I am here. We can go slowly. What is the smallest thing you want help carrying right now?"})
            save_state(self.state)

        chat_outer = tk.Frame(self.content, bg=SOFT, highlightbackground=LINE, highlightthickness=1)
        chat_outer.pack(fill="both", expand=True, pady=(0, 12))
        chat_canvas = tk.Canvas(chat_outer, bg=SOFT, highlightthickness=0)
        chat_scrollbar = tk.Scrollbar(chat_outer, orient="vertical", command=chat_canvas.yview)
        chat_messages = tk.Frame(chat_canvas, bg=SOFT)
        chat_window = chat_canvas.create_window((0, 0), window=chat_messages, anchor="nw")
        chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        chat_canvas.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")

        def resize_messages(event):
            chat_canvas.itemconfigure(chat_window, width=event.width)

        def update_scroll_region(event=None):
            chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

        chat_canvas.bind("<Configure>", resize_messages)
        chat_messages.bind("<Configure>", update_scroll_region)
        for message in self.state["chat"]:
            self.chat_bubble(chat_messages, message)
        self.root.after(80, lambda: chat_canvas.yview_moveto(1.0))

        bottom = tk.Frame(self.content, bg=BACKGROUND)
        bottom.pack(fill="x")
        entry = tk.Text(bottom, height=3, wrap="word", relief="flat", highlightbackground=LINE, highlightthickness=1)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def send():
            text = entry.get("1.0", "end").strip()
            if not text:
                return
            crisis = any(re.search(pattern, text, re.IGNORECASE) for pattern in CRISIS_PATTERNS)
            self.state["chat"].append({"role": "user", "text": text})
            self.state["chat"].append({"role": "bot", "text": self.companion_reply(text, crisis)})
            self.state["chat"] = self.state["chat"][-80:]
            save_state(self.state)
            if crisis:
                self.show_crisis_dialog()
            self.show_shell("chat")

        self.button(bottom, "Send", send).pack(side="right")

    def chat_bubble(self, parent, message):
        role = message.get("role", "bot")
        is_user = role == "user"
        row = tk.Frame(parent, bg=SOFT)
        row.pack(fill="x", padx=14, pady=7)

        bubble_bg = TITLE if is_user else BACKGROUND
        bubble_fg = "white" if is_user else TEXT
        name = "You" if is_user else APP_NAME
        side = "right" if is_user else "left"
        anchor = "e" if is_user else "w"

        bubble = tk.Frame(row, bg=bubble_bg, padx=14, pady=10, highlightbackground=LINE, highlightthickness=0)
        bubble.pack(side=side, anchor=anchor)
        tk.Label(
            bubble,
            text=name,
            fg=bubble_fg,
            bg=bubble_bg,
            font=("Google Sans", 9, "bold"),
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            bubble,
            text=message.get("text", ""),
            fg=bubble_fg,
            bg=bubble_bg,
            font=("Google Sans", 11),
            wraplength=560,
            justify="left",
        ).pack(anchor="w")

    def companion_reply(self, text, crisis):
        lower = text.lower()
        if crisis:
            return "I am taking this seriously. Move near another person if you can and contact 9-8-8 now. I can stay with you for one grounding step too."
        if any(word in lower for word in ["panic", "anxious", "anxiety", "overwhelmed", "flashback", "scared"]):
            return "Let us shrink the moment. Name five things you can see, then press your feet into the floor and exhale longer than you inhale."
        if any(word in lower for word in ["sad", "alone", "lonely", "worthless", "ashamed", "cry", "tired"]):
            return "That sounds heavy. You do not have to turn it into a perfect sentence. Tell me one detail of what hurts most right now."
        if any(word in lower for word in ["study", "school", "work", "career", "goal", "future", "job"]):
            return "A future can start very small. Choose one step that takes less than ten minutes, then let that count."
        return "I hear you. Let us make this moment smaller: what is one thing your body needs in the next five minutes?"

    def show_crisis_dialog(self):
        modal = tk.Toplevel(self.root)
        modal.title("Emergency help")
        modal.configure(bg=BACKGROUND)
        modal.geometry("560x330")
        modal.transient(self.root)
        modal.grab_set()
        tk.Label(modal, text="You do not have to handle this alone.", fg=TITLE, bg=BACKGROUND, font=("Avenir Next", 22, "bold")).pack(anchor="w", padx=24, pady=(24, 8))
        tk.Label(modal, text="If there is immediate danger, call emergency services now. For suicide crisis support in Canada, contact 9-8-8.", fg=TEXT, bg=BACKGROUND, wraplength=500, justify="left").pack(anchor="w", padx=24)
        row = tk.Frame(modal, bg=BACKGROUND)
        row.pack(anchor="w", padx=24, pady=18)
        self.button(row, "Call 988", lambda: webbrowser.open("tel:988")).pack(side="left", padx=(0, 8))
        self.button(row, "Text 988", lambda: webbrowser.open("sms:988"), bg=OPTION_BUTTON, fg=NAVY).pack(side="left", padx=(0, 8))
        self.button(row, "988.ca", lambda: webbrowser.open("https://988.ca/"), bg=OPTION_BUTTON, fg=NAVY).pack(side="left")
        self.button(modal, "Ground for one minute", lambda: [modal.destroy(), self.show_shell("exercises")], bg=OPTION_BUTTON, fg=NAVY).pack(anchor="w", padx=24)
        self.button(modal, "I am safe for now", modal.destroy, bg=BACKGROUND, fg=NAVY).pack(anchor="e", padx=24, pady=16)

    def page_emergency(self):
        self.page_title("Urgent care", "Emergency help")
        box = tk.Frame(self.content, bg=SOFT, padx=20, pady=20, highlightbackground=LINE, highlightthickness=1)
        box.pack(fill="x", pady=(0, 14))
        tk.Label(box, text="9-8-8: Suicide Crisis Helpline", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        tk.Label(box, text="Live support by phone and text across Canada, in English and French, 24 hours a day.", fg=TEXT, bg=SOFT, wraplength=780, justify="left").pack(anchor="w", pady=8)
        row = tk.Frame(box, bg=SOFT)
        row.pack(anchor="w")
        self.button(row, "Call 988", lambda: webbrowser.open("tel:988")).pack(side="left", padx=(0, 8))
        self.button(row, "Text 988", lambda: webbrowser.open("sms:988"), bg=OPTION_BUTTON, fg=NAVY).pack(side="left", padx=(0, 8))
        self.button(row, "Open 988.ca", lambda: webbrowser.open("https://988.ca/"), bg=OPTION_BUTTON, fg=NAVY).pack(side="left")

        plan = tk.Frame(self.content, bg=SOFT, padx=20, pady=20, highlightbackground=LINE, highlightthickness=1)
        plan.pack(fill="x")
        tk.Label(plan, text="Safety plan", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).grid(row=0, column=0, sticky="w", columnspan=2)
        fields = [("trusted", "Trusted person"), ("place", "Safe place"), ("action", "Calming action")]
        entries = {}
        for row_index, (key, label) in enumerate(fields, start=1):
            tk.Label(plan, text=label, fg=NAVY, bg=SOFT).grid(row=row_index, column=0, sticky="w", pady=8)
            entry = tk.Entry(plan, relief="flat", highlightbackground=LINE, highlightthickness=1)
            entry.insert(0, self.state["safety"].get(key, ""))
            entry.grid(row=row_index, column=1, sticky="ew", pady=8, ipady=6)
            entries[key] = entry
        plan.columnconfigure(1, weight=1)

        def save_plan():
            self.state["safety"] = {key: entry.get().strip() for key, entry in entries.items()}
            save_state(self.state)
            messagebox.showinfo(APP_NAME, "Saved.")

        self.button(plan, "Save plan", save_plan).grid(row=4, column=1, sticky="e", pady=8)

    def page_journal(self):
        self.page_title("Private space", "Encrypted journal")
        body = tk.Frame(self.content, bg=BACKGROUND)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Journal PIN", fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w")
        pin = tk.Entry(left, show="*", relief="flat", highlightbackground=LINE, highlightthickness=1)
        pin.pack(fill="x", ipady=7, pady=(4, 12))
        tk.Label(left, text="Entry", fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w")
        entry = tk.Text(left, height=12, wrap="word", relief="flat", highlightbackground=LINE, highlightthickness=1)
        entry.pack(fill="both", expand=True, pady=(4, 12))

        def save_entry():
            value = entry.get("1.0", "end").strip()
            if len(pin.get()) < 4 or not value:
                messagebox.showwarning(APP_NAME, "Enter a PIN with at least 4 digits and a journal entry.")
                return
            encrypted = encrypt_note(pin.get(), value)
            encrypted["time"] = time.time()
            self.state["journal"].insert(0, encrypted)
            save_state(self.state)
            self.show_shell("journal")

        self.button(left, "Save encrypted entry", save_entry).pack(anchor="e")
        tk.Label(right, text="Entries", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        output = scrolledtext.ScrolledText(right, height=18, wrap="word", relief="flat", highlightbackground=LINE, highlightthickness=1)
        output.pack(fill="both", expand=True, pady=8)
        output.insert("end", "Entries are encrypted. Enter your PIN on the left and unlock them here.\n")
        output.configure(state="disabled")

        def unlock():
            output.configure(state="normal")
            output.delete("1.0", "end")
            try:
                for item in self.state["journal"]:
                    text = decrypt_note(pin.get(), item)
                    stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["time"]))
                    output.insert("end", f"{stamp}\n{text}\n\n")
                if not self.state["journal"]:
                    output.insert("end", "No entries yet.")
            except Exception:
                output.insert("end", "That PIN did not unlock the entries.")
            output.configure(state="disabled")

        self.button(right, "Unlock", unlock, bg=OPTION_BUTTON, fg=NAVY).pack(anchor="e")

    def page_exercises(self):
        self.page_title("Body and mind", "Recovery exercises")
        body = tk.Frame(self.content, bg=BACKGROUND)
        body.pack(fill="both", expand=True)
        for col in range(3):
            body.columnconfigure(col, weight=1)
        self.exercise_breathing(body, 0)
        self.exercise_grounding(body, 1)
        self.exercise_triggers(body, 2)

    def exercise_breathing(self, parent, col):
        frame = tk.Frame(parent, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        frame.grid(row=0, column=col, sticky="nsew", padx=8)
        tk.Label(frame, text="Breathing", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        canvas = tk.Canvas(frame, width=190, height=190, bg=SOFT, highlightthickness=0)
        canvas.pack(pady=18)
        circle = canvas.create_oval(25, 25, 165, 165, outline=TITLE, width=3, fill=BACKGROUND)
        label = canvas.create_text(95, 95, text="Inhale", fill=NAVY, font=("Avenir Next", 17, "bold"))

        def step():
            if not self.breathing:
                return
            phases = ["Inhale", "Hold", "Exhale", "Rest"]
            self.breath_phase = (self.breath_phase + 1) % len(phases)
            canvas.itemconfigure(label, text=phases[self.breath_phase])
            radius = 70 if phases[self.breath_phase] in ["Inhale", "Hold"] else 55
            canvas.coords(circle, 95 - radius, 95 - radius, 95 + radius, 95 + radius)
            self.root.after(2200, step)

        def start_stop():
            self.breathing = not self.breathing
            if self.breathing:
                self.state["skills"]["breathing"] += 1
                save_state(self.state)
                step()
            else:
                canvas.itemconfigure(label, text="Inhale")

        self.button(frame, "Start / Stop", start_stop).pack()

    def exercise_grounding(self, parent, col):
        frame = tk.Frame(parent, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        frame.grid(row=0, column=col, sticky="nsew", padx=8)
        tk.Label(frame, text="5-4-3-2-1", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        prompt = tk.Label(frame, text=GROUNDING_PROMPTS[self.grounding_index], fg=TEXT, bg=BACKGROUND, wraplength=270, justify="left", padx=12, pady=18)
        prompt.pack(fill="x", pady=18)

        def next_prompt():
            self.grounding_index = (self.grounding_index + 1) % len(GROUNDING_PROMPTS)
            self.state["skills"]["grounding"] += 1
            save_state(self.state)
            prompt.configure(text=GROUNDING_PROMPTS[self.grounding_index])

        self.button(frame, "Next", next_prompt, bg=OPTION_BUTTON, fg=NAVY).pack()

    def exercise_triggers(self, parent, col):
        frame = tk.Frame(parent, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        frame.grid(row=0, column=col, sticky="nsew", padx=8)
        tk.Label(frame, text="Trigger map", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        entry = tk.Entry(frame, relief="flat", highlightbackground=LINE, highlightthickness=1)
        entry.pack(fill="x", ipady=7, pady=(12, 8))

        def add_trigger():
            text = entry.get().strip()
            if text:
                self.state["triggers"].insert(0, text)
                self.state["triggers"] = self.state["triggers"][:24]
                save_state(self.state)
                self.show_shell("exercises")

        self.button(frame, "Add", add_trigger, bg=OPTION_BUTTON, fg=NAVY).pack(anchor="e")
        for item in self.state["triggers"][:10]:
            tk.Label(frame, text=item, fg=NAVY, bg=OPTION_BUTTON, padx=10, pady=5).pack(anchor="w", pady=3)

    def page_goals(self):
        self.page_title("Future", "Goals and planning")
        body = tk.Frame(self.content, bg=BACKGROUND)
        body.pack(fill="both", expand=True)
        form = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        form.pack(side="left", fill="both", expand=True, padx=(0, 12))
        listing = tk.Frame(body, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
        listing.pack(side="left", fill="both", expand=True)
        fields = {}
        for label in ["Goal", "Next step", "Strength used"]:
            tk.Label(form, text=label, fg=NAVY, bg=SOFT, font=("Google Sans", 11, "bold")).pack(anchor="w")
            field = tk.Entry(form, relief="flat", highlightbackground=LINE, highlightthickness=1)
            field.pack(fill="x", ipady=7, pady=(4, 12))
            fields[label] = field

        def save_goal():
            goal = fields["Goal"].get().strip()
            step = fields["Next step"].get().strip()
            strength = fields["Strength used"].get().strip()
            if not goal or not step:
                messagebox.showwarning(APP_NAME, "Add a goal and next step.")
                return
            self.state["goals"].insert(0, {"goal": goal, "step": step, "strength": strength, "time": time.time()})
            save_state(self.state)
            self.show_shell("goals")

        self.button(form, "Save goal", save_goal).pack(anchor="e")
        tk.Label(listing, text="Active goals", fg=NAVY, bg=SOFT, font=("Google Sans", 14, "bold")).pack(anchor="w")
        if not self.state["goals"]:
            tk.Label(listing, text="No goals yet.", fg=MUTED, bg=SOFT).pack(anchor="w", pady=8)
        for index, goal in enumerate(self.state["goals"]):
            box = tk.Frame(listing, bg=BACKGROUND, padx=10, pady=10, highlightbackground=LINE, highlightthickness=1)
            box.pack(fill="x", pady=6)
            tk.Label(box, text=goal["goal"], fg=NAVY, bg=BACKGROUND, font=("Google Sans", 11, "bold")).pack(anchor="w")
            tk.Label(box, text=goal["step"], fg=TEXT, bg=BACKGROUND, wraplength=420, justify="left").pack(anchor="w")
            if goal.get("strength"):
                tk.Label(box, text=goal["strength"], fg=MUTED, bg=BACKGROUND).pack(anchor="w")
            row = tk.Frame(box, bg=BACKGROUND)
            row.pack(anchor="e")
            self.button(row, "Complete", lambda index=index: self.complete_goal(index), bg=OPTION_BUTTON, fg=NAVY).pack(side="left", padx=4)
            self.button(row, "Remove", lambda index=index: self.remove_goal(index), bg=BACKGROUND, fg=NAVY).pack(side="left", padx=4)

    def complete_goal(self, index):
        if 0 <= index < len(self.state["goals"]):
            self.state["goals"].pop(index)
            self.state["completed_goals"] += 1
            save_state(self.state)
        self.show_shell("goals")

    def remove_goal(self, index):
        if 0 <= index < len(self.state["goals"]):
            self.state["goals"].pop(index)
            save_state(self.state)
        self.show_shell("goals")

    def page_dashboard(self):
        self.page_title("Progress", "Your dashboard", "Progress is cumulative here. Nothing is lost when a week is difficult.")
        stats = [
            ("Mood check-ins", len(self.state["moods"])),
            ("Journal entries", len(self.state["journal"])),
            ("Goals achieved", self.state["completed_goals"]),
            ("Exercises completed", self.state["skills"]["breathing"] + self.state["skills"]["grounding"]),
            ("Triggers mapped", len(self.state["triggers"])),
        ]
        grid = tk.Frame(self.content, bg=BACKGROUND)
        grid.pack(fill="x")
        for index, (label, value) in enumerate(stats):
            card = tk.Frame(grid, bg=SOFT, padx=18, pady=18, highlightbackground=LINE, highlightthickness=1)
            card.grid(row=0, column=index, sticky="nsew", padx=6)
            grid.columnconfigure(index, weight=1)
            tk.Label(card, text=str(value), fg=TITLE, bg=SOFT, font=("Avenir Next", 30, "bold")).pack(anchor="w")
            tk.Label(card, text=label, fg=NAVY, bg=SOFT, font=("Google Sans", 10, "bold"), wraplength=150).pack(anchor="w")

    def page_privacy(self):
        self.page_title(self.tr("settings"), self.tr("privacy_title"))
        box = tk.Frame(self.content, bg=SOFT, padx=20, pady=20, highlightbackground=LINE, highlightthickness=1)
        box.pack(fill="x")
        self.language_selector(box, refresh="privacy").pack(anchor="w", pady=(0, 8))
        tk.Label(box, text=self.tr("save_language"), fg=MUTED, bg=SOFT, wraplength=820, justify="left").pack(anchor="w", pady=(0, 12))
        tk.Label(box, text="Data stays on this computer in sobrad_data.json beside the Python app.", fg=TEXT, bg=SOFT, wraplength=820, justify="left").pack(anchor="w", pady=(0, 12))
        anonymous = tk.BooleanVar(value=self.state.get("anonymous", False))
        tk.Checkbutton(box, text="Anonymous mode", variable=anonymous, bg=SOFT, fg=NAVY, activebackground=SOFT).pack(anchor="w")

        def save_privacy():
            self.state["anonymous"] = anonymous.get()
            save_state(self.state)
            messagebox.showinfo(APP_NAME, "Saved.")

        def delete_all():
            if messagebox.askyesno(APP_NAME, "Delete all local SÕBRAD data from this computer?"):
                self.state = default_state()
                if DATA_FILE.exists():
                    DATA_FILE.unlink()
                self.show_login()

        row = tk.Frame(box, bg=SOFT)
        row.pack(anchor="w", pady=16)
        self.button(row, "Save privacy settings", save_privacy).pack(side="left", padx=(0, 8))
        self.button(row, "Delete all data", delete_all, bg=DANGER, fg="white").pack(side="left")


def main():
    root = tk.Tk()
    SobradApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
