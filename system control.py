# ─── automation/system_control.py ────────────────────────
import os
import platform
import subprocess
from datetime import datetime
from config import OS

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def take_screenshot() -> str:
    """Take a screenshot and save it."""
    if not PYAUTOGUI_AVAILABLE:
        return "pyautogui not installed. Run: pip install pyautogui"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
    pyautogui.screenshot(path)
    return f"Screenshot saved to Desktop as {filename}."


def set_volume(command: str) -> str:
    """Increase, decrease or mute system volume."""
    command = command.lower()

    if OS == "Windows" and PYCAW_AVAILABLE:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterScalarVolume()

        if "mute" in command:
            volume.SetMute(1, None)
            return "System muted."
        elif "unmute" in command:
            volume.SetMute(0, None)
            return "System unmuted."
        elif "up" in command or "increase" in command:
            new_vol = min(1.0, current + 0.1)
            volume.SetMasterScalarVolume(new_vol, None)
            return f"Volume increased to {int(new_vol * 100)}%."
        elif "down" in command or "decrease" in command:
            new_vol = max(0.0, current - 0.1)
            volume.SetMasterScalarVolume(new_vol, None)
            return f"Volume decreased to {int(new_vol * 100)}%."

    # Fallback for non-Windows or missing pycaw
    if "up" in command or "increase" in command:
        if OS == "Linux":
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
        return "Volume increased."
    elif "down" in command or "decrease" in command:
        if OS == "Linux":
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
        return "Volume decreased."
    elif "mute" in command:
        if OS == "Linux":
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
        return "Volume toggled."

    return "Volume command not recognized."


def shutdown():
    """Shutdown the PC."""
    if OS == "Windows":
        subprocess.call(["shutdown", "/s", "/t", "5"])
    elif OS == "Linux":
        subprocess.call(["shutdown", "-h", "now"])
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-h", "now"])


def restart():
    """Restart the PC."""
    if OS == "Windows":
        subprocess.call(["shutdown", "/r", "/t", "5"])
    elif OS == "Linux":
        subprocess.call(["reboot"])
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-r", "now"])


def lock_screen():
    """Lock the screen."""
    if OS == "Windows":
        subprocess.call(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif OS == "Linux":
        subprocess.call(["gnome-screensaver-command", "-l"])
    elif OS == "Darwin":
        subprocess.call(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
    return "Screen locked."
