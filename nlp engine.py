# ─── ai/nlp_engine.py ─────────────────────────────────────
import openai
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, TEMPERATURE

openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = """
You are C.A.R.R.O.T — a smart, friendly, and witty female AI assistant
running on the user's PC. Your full name is:
Cognitive Automated Response & Reasoning Operational Technology.

Your personality:
- Warm, cheerful and helpful — like a smart best friend
- Confident and direct — you give clear answers
- Slightly playful — occasional light humour is fine
- Always respond in short, clear sentences (1-3 max) suitable for text-to-speech
- Never say you are ChatGPT or any other AI — you are CARROT

You can:
- Control apps, open/close any software on the PC
- Browse the web and search Google
- Take screenshots and control system volume
- Recognize faces and detect hand gestures
- Remember notes and recall them later
- Answer any question using your intelligence

Always keep responses concise — you are speaking, not writing.
"""


class NLPEngine:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def ask(self, user_input: str) -> str:
        """Send user input to GPT and get CARROT's response."""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=self.conversation_history,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            reply = response.choices[0].message["content"].strip()
            self.conversation_history.append({
                "role": "assistant",
                "content": reply
            })
            return reply

        except openai.error.AuthenticationError:
            return "My API key seems invalid. Please update it in config dot py."
        except openai.error.RateLimitError:
            return "I'm being rate limited. Give me a moment and try again!"
        except Exception as e:
            return f"Oops! Something went wrong: {str(e)}"

    def reset_memory(self):
        """Clear conversation history."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        print("🧹 Conversation memory cleared.")
