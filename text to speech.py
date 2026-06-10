# ─── speech/text_to_speech.py ─────────────────────────────
# Female voice engine for C.A.R.R.O.T

import pyttsx3
import threading
from config import SPEECH_RATE, SPEECH_PITCH, ASSISTANT_NAME

engine = pyttsx3.init()


def _setup_female_voice(eng):
    """
    Automatically find and set the best female voice.
    Falls back to first available voice if no female found.
    """
    voices = eng.getProperty("voices")
    female_voice = None

    # Search for female voice by name keywords
    female_keywords = ["female", "woman", "girl", "zira", "hazel",
                       "susan", "karen", "samantha", "victoria",
                       "moira", "tessa", "fiona", "kate", "serena"]

    for voice in voices:
        voice_name = voice.name.lower()
        for keyword in female_keywords:
            if keyword in voice_name:
                female_voice = voice
                break
        if female_voice:
            break

    if female_voice:
        eng.setProperty("voice", female_voice.id)
        print(f"✅ Female voice selected: {female_voice.name}")
    else:
        # Fallback: try index 1 (usually female on most systems)
        if len(voices) > 1:
            eng.setProperty("voice", voices[1].id)
            print(f"⚠️  No female voice found by name. Using: {voices[1].name}")
        else:
            eng.setProperty("voice", voices[0].id)
            print(f"⚠️  Only one voice available: {voices[0].name}")

    # Set speed and pitch
    eng.setProperty("rate", SPEECH_RATE)

    # pyttsx3 pitch support varies by platform
    try:
        eng.setProperty("pitch", SPEECH_PITCH)
    except:
        pass   # Not all platforms support pitch

    return eng


# Setup engine with female voice
engine = _setup_female_voice(engine)


def speak(text: str, block=True):
    """
    Convert text to speech using Carrot's female voice.
    block=True  → wait until speech finishes
    block=False → speak in background thread
    """
    print(f"🥕 {ASSISTANT_NAME}: {text}")
    if block:
        engine.say(text)
        engine.runAndWait()
    else:
        t = threading.Thread(target=_speak_bg, args=(text,), daemon=True)
        t.start()


def _speak_bg(text: str):
    """Background speech using a fresh engine instance."""
    local_engine = pyttsx3.init()
    local_engine = _setup_female_voice(local_engine)
    local_engine.say(text)
    local_engine.runAndWait()


def list_available_voices():
    """Print all available voices on the system."""
    voices = engine.getProperty("voices")
    print(f"\n🎤 Available voices on your system ({len(voices)} total):")
    for i, voice in enumerate(voices):
        print(f"  [{i}] {voice.name} | ID: {voice.id}")
    print()
    return voices


def set_voice_by_index(index: int):
    """Manually switch voice by index number."""
    voices = engine.getProperty("voices")
    if 0 <= index < len(voices):
        engine.setProperty("voice", voices[index].id)
        print(f"✅ Voice changed to: {voices[index].name}")
    else:
        print(f"❌ Invalid index. Available: 0 to {len(voices)-1}")


def set_rate(rate: int):
    """Change speaking speed. Default=165. Faster=200, Slower=130."""
    engine.setProperty("rate", rate)
    print(f"✅ Speech rate set to {rate}")


def set_pitch(pitch: int):
    """Change pitch. Higher = more feminine. Default=200."""
    try:
        engine.setProperty("pitch", pitch)
        print(f"✅ Pitch set to {pitch}")
    except:
        print("⚠️  Pitch control not supported on this platform.")
