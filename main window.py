# ─── gui/main_window.py ───────────────────────────────────
import tkinter as tk
from tkinter import scrolledtext
import threading
from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, THEME_COLOR, BG_COLOR, ASSISTANT_NAME


class MainWindow:
    def __init__(self, chatbot, speech_input_fn):
        self.chatbot   = chatbot
        self.listen_fn = speech_input_fn

        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)

        self._build_ui()

    def _build_ui(self):
        # ── Title ─────────────────────────────────────────
        title = tk.Label(
            self.root,
            text="🥕 C.A.R.R.O.T",
            font=("Courier New", 24, "bold"),
            fg=THEME_COLOR, bg=BG_COLOR
        )
        title.pack(pady=(16, 2))

        subtitle = tk.Label(
            self.root,
            text="Cognitive Automated Response & Reasoning Operational Technology",
            font=("Courier New", 8),
            fg="#aa6688", bg=BG_COLOR
        )
        subtitle.pack(pady=(0, 10))

        # ── Chat display ───────────────────────────────────
        self.chat_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD,
            font=("Courier New", 11),
            bg="#0d0d1f", fg="#e0e0e0",
            insertbackground=THEME_COLOR,
            relief=tk.FLAT, padx=10, pady=10,
            height=18
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        self.chat_box.tag_config("user",   foreground=THEME_COLOR)
        self.chat_box.tag_config("carrot", foreground="#ffffff")
        self.chat_box.tag_config("system", foreground="#886688")
        self.chat_box.config(state=tk.DISABLED)

        # ── Input row ──────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill=tk.X, padx=16, pady=8)

        self.entry = tk.Entry(
            input_frame,
            font=("Courier New", 12),
            bg="#1a0a1a", fg=THEME_COLOR,
            insertbackground=THEME_COLOR,
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", self._on_type_send)

        send_btn = tk.Button(
            input_frame, text="Send",
            font=("Courier New", 11, "bold"),
            bg=THEME_COLOR, fg=BG_COLOR,
            relief=tk.FLAT, cursor="hand2",
            command=self._on_type_send
        )
        send_btn.pack(side=tk.LEFT, ipady=6, ipadx=10)

        self.mic_btn = tk.Button(
            input_frame, text="🎤",
            font=("Courier New", 14),
            bg="#1a0a1a", fg=THEME_COLOR,
            relief=tk.FLAT, cursor="hand2",
            command=self._on_mic_click
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(6, 0), ipady=4, ipadx=8)

        # ── Status bar ─────────────────────────────────────
        self.status_var = tk.StringVar(
            value=f"Ready. Say '{ASSISTANT_NAME}' or type a command."
        )
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Courier New", 9),
            fg="#885577", bg=BG_COLOR
        )
        status.pack(pady=(0, 8))

        self._add_message(
            "system",
            f"{ASSISTANT_NAME} is online! Hey there! I'm Carrot, your personal AI assistant. How can I help you today?"
        )

    def _add_message(self, role: str, text: str):
        self.chat_box.config(state=tk.NORMAL)
        prefix = {
            "user":   "You: ",
            "carrot": f"{ASSISTANT_NAME}: ",
            "system": "⚙ "
        }.get(role, "")
        self.chat_box.insert(tk.END, f"{prefix}{text}\n\n", role)
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def _on_type_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_message("user", text)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _on_mic_click(self):
        self.mic_btn.config(text="🔴", state=tk.DISABLED)
        self.status_var.set(f"{ASSISTANT_NAME} is listening...")
        threading.Thread(target=self._listen_and_process, daemon=True).start()

    def _listen_and_process(self):
        text = self.listen_fn()
        self.mic_btn.config(text="🎤", state=tk.NORMAL)
        if text:
            self._add_message("user", text)
            self._process(text)
        else:
            self.status_var.set("Hmm, I didn't catch that. Try again!")

    def _process(self, text: str):
        self.status_var.set(f"{ASSISTANT_NAME} is thinking...")
        response = self.chatbot.process(text)
        self._add_message("carrot", response)
        self.status_var.set("Ready.")

    def run(self):
        self.root.mainloop()
