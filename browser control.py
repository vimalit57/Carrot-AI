# ─── automation/browser_control.py ───────────────────────
import webbrowser
from config import DEFAULT_SEARCH_ENGINE


def search_web(query: str) -> str:
    """Search Google for a query."""
    if not query:
        return "Please tell me what to search for."
    url = DEFAULT_SEARCH_ENGINE + query.replace(" ", "+")
    webbrowser.open(url)
    return f"Searching for {query} on Google."


def open_url(url: str) -> str:
    """Open a specific URL in the browser."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url} in your browser."


def open_youtube(query: str = "") -> str:
    """Open YouTube with optional search query."""
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    else:
        url = "https://www.youtube.com"
    webbrowser.open(url)
    return f"Opening YouTube{' and searching for ' + query if query else ''}."


def open_gmail() -> str:
    webbrowser.open("https://mail.google.com")
    return "Opening Gmail."


def open_maps(location: str = "") -> str:
    if location:
        url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
    else:
        url = "https://www.google.com/maps"
    webbrowser.open(url)
    return f"Opening Google Maps{' for ' + location if location else ''}."
