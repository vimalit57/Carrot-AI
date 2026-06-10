# ─── ai/chatbot.py ────────────────────────────────────────
from datetime import datetime
from ai.nlp_engine import NLPEngine
from ai.intent_classifier import (classify_intent, extract_app_name,
                                   extract_search_query, extract_url)
from speech.text_to_speech import speak
from automation.app_control import (open_app, close_app, switch_to_app,
                                     list_installed_apps, rescan_apps)
from automation.browser_control import search_web, open_url
from automation.system_control import (take_screenshot, set_volume,
                                        shutdown, restart, lock_screen)
from database.memory import save_memory, recall_memory, clear_memory
from vision.face_recognition import recognize_from_camera
from vision.gesture_control import start_gesture_control


class Chatbot:
    def __init__(self):
        self.nlp = NLPEngine()
        self.running = True
        # Scan apps at startup in background
        import threading
        threading.Thread(target=self._preload_apps, daemon=True).start()

    def _preload_apps(self):
        """Preload app registry at startup silently."""
        from automation.app_control import _get_registry
        registry = _get_registry()
        print(f"✅ App registry ready: {len(registry)} apps available.")

    def process(self, user_input: str) -> str:
        if not user_input:
            return ""

        intent, text = classify_intent(user_input)
        print(f"🧠 Intent: {intent}")

        if intent == "greet":
            hour = datetime.now().hour
            if hour < 12:   response = "Good morning! How can I assist you?"
            elif hour < 17: response = "Good afternoon! What can I do for you?"
            else:           response = "Good evening! I'm ready to help."
            speak(response); return response

        elif intent == "open_app":
            app = extract_app_name(text)
            result = open_app(app)
            speak(result); return result

        elif intent == "close_app":
            app = extract_app_name(text)
            result = close_app(app)
            speak(result); return result

        elif intent == "switch_app":
            app = extract_app_name(text)
            result = switch_to_app(app)
            speak(result); return result

        elif intent == "list_apps":
            apps = list_installed_apps()
            response = f"You have {len(apps)} installed apps. Some include: {', '.join(apps[:10])}."
            speak(response); return response

        elif intent == "rescan_apps":
            speak("Scanning your entire system for installed apps. Please wait.")
            result = rescan_apps()
            speak(result); return result

        elif intent == "search_web":
            query = extract_search_query(text)
            result = search_web(query)
            speak(result); return result

        elif intent == "open_url":
            url = extract_url(text)
            result = open_url(url)
            speak(result); return result

        elif intent == "take_screenshot":
            result = take_screenshot()
            speak(result); return result

        elif intent == "system_volume":
            result = set_volume(text)
            speak(result); return result

        elif intent == "system_shutdown":
            speak("Shutting down your system. Goodbye!")
            shutdown(); return "Shutting down..."

        elif intent == "lock_screen":
            result = lock_screen()
            speak(result); return result

        elif intent == "tell_time":
            now = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {now}."
            speak(response); return response

        elif intent == "tell_date":
            today = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {today}."
            speak(response); return response

        elif intent == "face_recognition":
            speak("Starting face recognition. Please look at the camera.")
            result = recognize_from_camera()
            speak(result); return result

        elif intent == "gesture_control":
            speak("Activating gesture control mode.")
            start_gesture_control()
            return "Gesture control started."

        elif intent == "remember":
            data = text.replace("remember", "").replace("save this", "").replace("make a note", "").strip()
            save_memory(data)
            response = f"Got it! Saved to memory: {data}"
            speak(response); return response

        elif intent == "recall":
            memories = recall_memory()
            response = f"You asked me to remember: {', '.join(memories)}" if memories else "Nothing saved in memory yet."
            speak(response); return response

        elif intent == "clear_memory":
            clear_memory()
            self.nlp.reset_memory()
            response = "Memory cleared. Starting fresh!"
            speak(response); return response

        elif intent == "stop":
            self.running = False
            response = "Going to sleep. Say Jarvis to wake me up!"
            speak(response); return response

        else:
            response = self.nlp.ask(user_input)
            speak(response); return response

    def is_running(self):
        return self.running
