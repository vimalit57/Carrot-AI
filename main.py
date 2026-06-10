# ─── main.py ──────────────────────────────────────────────
# C.A.R.R.O.T — Female AI Assistant
# Run: python main.py

import threading
from config import ASSISTANT_NAME
from speech.text_to_speech import speak, list_available_voices
from speech.speech_to_text import listen, wait_for_wake_word
from ai.chatbot import Chatbot
from gui.main_window import MainWindow


def main():
    print("=" * 55)
    print(f"   {ASSISTANT_NAME} — Female AI Assistant Starting...")
    print("=" * 55)

    # Optional: print all available voices
    list_available_voices()

    # Init chatbot
    bot = Chatbot()

    # Startup greeting (female voice)
    speak(f"Hi! I'm {ASSISTANT_NAME}, your personal AI assistant. "
          f"I'm all set and ready to help you. "
          f"Just say my name to get started!")

    # Launch GUI
    window = MainWindow(chatbot=bot, speech_input_fn=listen)

    # Background voice loop
    def voice_loop():
        while True:
            wait_for_wake_word()
            speak("Yes? I'm listening!")
            text = listen(timeout=8)
            if text:
                response = bot.process(text)
                window._add_message("user", text)
                window._add_message("carrot", response)

    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    # Start GUI (blocking)
    window.run()


if __name__ == "__main__":
    main()
