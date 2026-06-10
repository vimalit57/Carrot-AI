# ─── config.py ────────────────────────────────────────────
# Central configuration for CARROT AI Assistant

# OpenAI
OPENAI_API_KEY = "your-openai-api-key-here"
GPT_MODEL      = "gpt-4"
MAX_TOKENS     = 1024
TEMPERATURE    = 0.7

# Assistant Identity
ASSISTANT_NAME = "Carrot"
WAKE_WORD      = "carrot"        # say "carrot" to wake her up

# Speech
SPEECH_LANGUAGE = "en-US"
TTS_VOICE       = "en"
SPEECH_RATE     = 165            # slightly faster = more natural female tone
SPEECH_PITCH    = 200            # higher pitch for female voice (pyttsx3)
VOICE_GENDER    = "female"       # female | male

# Face Recognition
FACE_TOLERANCE   = 0.5
KNOWN_FACES_DIR  = "assets/known_faces"

# Gesture Control
GESTURE_CONFIDENCE = 0.7
CAM_INDEX          = 0

# Browser
DEFAULT_BROWSER       = "chrome"
DEFAULT_SEARCH_ENGINE = "https://www.google.com/search?q="

# App Paths
import platform
OS = platform.system()

APP_PATHS = {
    "notepad":    "notepad.exe"   if OS == "Windows" else "gedit",
    "calculator": "calc.exe"      if OS == "Windows" else "gnome-calculator",
    "chrome":     "chrome"        if OS != "Windows" else "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "vscode":     "code",
}

# Memory / Database
DB_PATH = "database/memory.db"

# GUI
WINDOW_TITLE  = "C.A.R.R.O.T"
WINDOW_WIDTH  = 900
WINDOW_HEIGHT = 600
THEME_COLOR   = "#FF6B9D"    # pink for Carrot 💗
BG_COLOR      = "#0a0a1a"    # dark navy
