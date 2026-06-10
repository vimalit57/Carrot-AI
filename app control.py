# ─── automation/app_control.py ────────────────────────────
# Full system app scanner + controller
# Scans ALL installed apps like Google Assistant

import os
import subprocess
import psutil
import json
import platform
from config import OS

# ── App Registry Cache path ───────────────────────────────
APP_CACHE_FILE = "database/app_registry.json"


# ─────────────────────────────────────────────────────────
# SECTION 1 — SYSTEM SCANNER
# Scans entire PC and builds an app registry
# ─────────────────────────────────────────────────────────

def scan_windows_registry() -> dict:
    """
    Scan Windows Registry for all installed applications.
    Covers both 32-bit and 64-bit installed apps.
    """
    apps = {}
    try:
        import winreg
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

        for hive in hives:
            for reg_path in registry_paths:
                try:
                    reg = winreg.OpenKey(hive, reg_path)
                    for i in range(winreg.QueryInfoKey(reg)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(reg, i)
                            sub_key = winreg.OpenKey(reg, sub_key_name)
                            try:
                                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                try:
                                    exe = winreg.QueryValueEx(sub_key, "DisplayIcon")[0]
                                    exe = exe.split(",")[0].strip().strip('"')
                                except:
                                    exe = ""
                                if name and exe and os.path.exists(exe):
                                    apps[name.lower()] = exe
                            except:
                                pass
                            winreg.CloseKey(sub_key)
                        except:
                            pass
                    winreg.CloseKey(reg)
                except:
                    pass
    except ImportError:
        pass
    return apps


def scan_windows_start_menu() -> dict:
    """
    Scan Windows Start Menu shortcuts (.lnk files).
    Covers apps that don't appear in registry.
    """
    apps = {}
    start_menu_dirs = [
        os.path.join(os.environ.get("APPDATA", ""),
                     "Microsoft", "Windows", "Start Menu", "Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    ]
    for directory in start_menu_dirs:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".lnk"):
                    name = file.replace(".lnk", "").lower()
                    full_path = os.path.join(root, file)
                    apps[name] = full_path
    return apps


def scan_windows_program_files() -> dict:
    """
    Deep scan Program Files directories for .exe files.
    """
    apps = {}
    scan_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Local", "Programs"),
    ]
    for directory in scan_dirs:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            # Limit depth for performance
            depth = root.replace(directory, "").count(os.sep)
            if depth > 3:
                dirs.clear()
                continue
            for file in files:
                if file.endswith(".exe"):
                    name = file.replace(".exe", "").lower()
                    full_path = os.path.join(root, file)
                    apps[name] = full_path
    return apps


def scan_linux_apps() -> dict:
    """
    Scan Linux .desktop files for all installed apps.
    Also checks common binary paths.
    """
    apps = {}

    # Scan .desktop files
    desktop_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/snapd/desktop/applications",   # Snap apps
        "/var/lib/flatpak/exports/share/applications",  # Flatpak apps
    ]
    for directory in desktop_dirs:
        if not os.path.exists(directory):
            continue
        for file in os.listdir(directory):
            if file.endswith(".desktop"):
                path = os.path.join(directory, file)
                name, exec_cmd = "", ""
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Name=") and not name:
                                name = line.strip().split("=", 1)[1].lower()
                            elif line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.strip().split("=", 1)[1]
                                exec_cmd = exec_cmd.split()[0]
                    if name and exec_cmd:
                        apps[name] = exec_cmd
                except:
                    pass

    # Also scan binaries in PATH
    for path_dir in ["/usr/bin", "/usr/local/bin", "/bin"]:
        if os.path.exists(path_dir):
            for binary in os.listdir(path_dir):
                full = os.path.join(path_dir, binary)
                if os.access(full, os.X_OK) and not os.path.isdir(full):
                    apps[binary.lower()] = full

    return apps


def scan_mac_apps() -> dict:
    """
    Scan macOS Applications folders.
    Also scans Homebrew and user-installed apps.
    """
    apps = {}
    app_dirs = [
        "/Applications",
        os.path.expanduser("~/Applications"),
        "/System/Applications",
    ]
    for directory in app_dirs:
        if not os.path.exists(directory):
            continue
        for item in os.listdir(directory):
            if item.endswith(".app"):
                name = item.replace(".app", "").lower()
                apps[name] = os.path.join(directory, item)

    # Homebrew binaries
    brew_bin = "/usr/local/bin"
    if os.path.exists(brew_bin):
        for binary in os.listdir(brew_bin):
            full = os.path.join(brew_bin, binary)
            if os.access(full, os.X_OK):
                apps[binary.lower()] = full

    return apps


def scan_all_apps(force_rescan=False) -> dict:
    """
    Master scanner — detects OS and scans ALL installed apps.
    Caches result to database/app_registry.json for speed.
    Returns dict: { app_name_lower: executable_path }

    Sources scanned:
    - Windows: Registry (32+64 bit), Start Menu, Program Files
    - Linux:   .desktop files, Snap, Flatpak, PATH binaries
    - Mac:     /Applications, ~/Applications, Homebrew
    """
    os.makedirs("database", exist_ok=True)

    # Return cached version if available
    if os.path.exists(APP_CACHE_FILE) and not force_rescan:
        try:
            with open(APP_CACHE_FILE, "r") as f:
                cached = json.load(f)
            print(f"📦 Loaded {len(cached)} apps from cache.")
            return cached
        except:
            pass

    print(f"🔍 Scanning entire system for installed apps on {OS}...")
    all_apps = {}

    if OS == "Windows":
        print("  → Scanning Windows Registry...")
        all_apps.update(scan_windows_registry())
        print(f"     Found {len(all_apps)} from registry")

        print("  → Scanning Start Menu...")
        sm = scan_windows_start_menu()
        all_apps.update(sm)
        print(f"     Found {len(sm)} from start menu")

        print("  → Scanning Program Files...")
        pf = scan_windows_program_files()
        all_apps.update(pf)
        print(f"     Found {len(pf)} from program files")

    elif OS == "Linux":
        print("  → Scanning .desktop files, Snap, Flatpak, PATH...")
        all_apps.update(scan_linux_apps())

    elif OS == "Darwin":
        print("  → Scanning /Applications and Homebrew...")
        all_apps.update(scan_mac_apps())

    # Save to cache
    with open(APP_CACHE_FILE, "w") as f:
        json.dump(all_apps, f, indent=2)

    print(f"\n✅ Scan complete! Found {len(all_apps)} apps. Cached to {APP_CACHE_FILE}")
    return all_apps


# ─────────────────────────────────────────────────────────
# SECTION 2 — SMART FUZZY MATCHER
# Matches voice command to closest installed app name
# ─────────────────────────────────────────────────────────

def find_best_match(app_name: str, app_registry: dict) -> tuple:
    """
    Smart fuzzy match — finds best app from registry.
    Returns (matched_name, executable_path) or ("", "")

    Priority levels:
    1. Exact match          → "chrome"       matches "chrome"
    2. Starts with query    → "chro"         matches "chrome"
    3. Contains query       → "oogle chr"    matches "google chrome"
    4. All words match      → "google chrome" matches "google chrome browser"
    5. Any key word match   → "chrome"       matches "google chrome"
    """
    query = app_name.lower().strip()

    # Level 1 — Exact
    if query in app_registry:
        return query, app_registry[query]

    # Level 2 — Starts with
    for name, path in app_registry.items():
        if name.startswith(query):
            return name, path

    # Level 3 — Name contains query
    for name, path in app_registry.items():
        if query in name:
            return name, path

    # Level 4 — All words of query in name
    words = [w for w in query.split() if len(w) > 2]
    if words:
        for name, path in app_registry.items():
            if all(w in name for w in words):
                return name, path

    # Level 5 — Any significant word matches
    for name, path in app_registry.items():
        if any(w in name for w in words if len(w) > 3):
            return name, path

    return "", ""


# ─────────────────────────────────────────────────────────
# SECTION 3 — APP CONTROLLER
# ─────────────────────────────────────────────────────────

# Global registry — loaded once at startup
_APP_REGISTRY = {}


def _get_registry() -> dict:
    global _APP_REGISTRY
    if not _APP_REGISTRY:
        _APP_REGISTRY = scan_all_apps()
    return _APP_REGISTRY


def open_app(app_name: str) -> str:
    """
    Open any installed application by voice command name.
    Automatically finds the best matching app.

    Examples:
        open_app("chrome")       → opens Google Chrome
        open_app("vs code")      → opens Visual Studio Code
        open_app("vlc")          → opens VLC Media Player
        open_app("spotify")      → opens Spotify
        open_app("word")         → opens Microsoft Word
    """
    app_name = app_name.lower().strip()
    registry = _get_registry()

    matched_name, exec_path = find_best_match(app_name, registry)

    if not matched_name:
        # Last resort: try running it directly as shell command
        try:
            subprocess.Popen(app_name, shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return f"Trying to open {app_name} directly."
        except:
            return (f"Sorry, I couldn't find '{app_name}' on your system. "
                    f"Try saying 'rescan apps' to refresh the app list.")

    try:
        if OS == "Windows":
            if exec_path.endswith(".lnk"):
                os.startfile(exec_path)
            else:
                subprocess.Popen([exec_path],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)

        elif OS == "Linux":
            subprocess.Popen([exec_path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

        elif OS == "Darwin":
            if exec_path.endswith(".app"):
                subprocess.Popen(["open", exec_path])
            else:
                subprocess.Popen([exec_path],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)

        return f"Opening {matched_name}."

    except Exception as e:
        return f"Found {matched_name} but couldn't launch it. Error: {e}"


def close_app(app_name: str) -> str:
    """
    Close any running application by name.
    Uses psutil to find and kill the process.
    """
    app_name = app_name.lower().strip()
    killed = []
    words  = [w for w in app_name.split() if len(w) > 3]

    for proc in psutil.process_iter(['name', 'pid']):
        try:
            proc_name = proc.info['name'].lower()
            if (app_name in proc_name or
                    any(w in proc_name for w in words)):
                proc.kill()
                killed.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if killed:
        return f"Closed: {', '.join(set(killed))}."
    return f"No running process found for '{app_name}'."


def list_running_apps() -> list:
    """Return names of all currently running processes."""
    apps = set()
    for proc in psutil.process_iter(['name']):
        try:
            apps.add(proc.info['name'])
        except psutil.NoSuchProcess:
            pass
    return sorted(list(apps))


def list_installed_apps(search: str = "") -> list:
    """
    Return all installed app names from registry.
    Optionally filter by search keyword.
    """
    registry = _get_registry()
    if search:
        return [name for name in registry.keys()
                if search.lower() in name]
    return sorted(list(registry.keys()))


def rescan_apps() -> str:
    """Force a full rescan of all installed apps on the system."""
    global _APP_REGISTRY
    _APP_REGISTRY = scan_all_apps(force_rescan=True)
    return f"Rescan complete! Found {len(_APP_REGISTRY)} installed apps."


def switch_to_app(app_name: str) -> str:
    """
    Bring a running app window to foreground.
    Falls back to opening the app if not running.
    """
    if OS == "Windows":
        try:
            import pygetwindow as gw
            wins = gw.getAllTitles()
            for title in wins:
                if app_name.lower() in title.lower():
                    win = gw.getWindowsWithTitle(title)
                    if win:
                        win[0].activate()
                        return f"Switched to {title}."
        except ImportError:
            pass

    # Fallback: open the app
    return open_app(app_name)
