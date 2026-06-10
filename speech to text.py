# ─── speech/speech_to_text.py ─────────────────────────────
import speech_recognition as sr
from config import SPEECH_LANGUAGE, WAKE_WORD, ASSISTANT_NAME

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0
recognizer.energy_threshold = 300


def listen(timeout=5, phrase_limit=10, prompt=True) -> str:
    """
    Listen from microphone and return recognised text.
    Returns None on failure.
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        if prompt:
            print(f"🎤 {ASSISTANT_NAME} is listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout,
                                      phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None


def wait_for_wake_word() -> bool:
    """
    Keeps listening until wake word 'carrot' is detected.
    Returns True when detected.
    """
    print(f"⏳ Say '{WAKE_WORD}' to wake {ASSISTANT_NAME}...")
    while True:
        text = listen(timeout=10, phrase_limit=5, prompt=False)
        if text and WAKE_WORD in text:
            print(f"✅ Wake word '{WAKE_WORD}' detected!")
            return True
