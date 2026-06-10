# ─── database/memory.py ───────────────────────────────────
import sqlite3
import os
from datetime import datetime
from config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables if they don't exist."""
    conn = _connect()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            data      TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            role      TEXT NOT NULL,
            message   TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_memory(data: str):
    """Save a memory note."""
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT INTO memory (data, timestamp) VALUES (?, ?)",
              (data, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"💾 Saved to memory: {data}")


def recall_memory(limit: int = 5) -> list:
    """Retrieve recent memory notes."""
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT data FROM memory ORDER BY id DESC LIMIT ?", (limit,))
    rows = [row[0] for row in c.fetchall()]
    conn.close()
    return rows


def clear_memory():
    """Clear all memory notes."""
    conn = _connect()
    c = conn.cursor()
    c.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    print("🧹 Memory cleared.")


def save_chat(role: str, message: str):
    """Log a chat message."""
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, message, timestamp) VALUES (?, ?, ?)",
              (role, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 20) -> list:
    """Get recent chat history as list of dicts."""
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM chat_history ORDER BY id DESC LIMIT ?",
              (limit,))
    rows = [{"role": r[0], "message": r[1], "time": r[2]} for r in c.fetchall()]
    conn.close()
    return list(reversed(rows))


# Auto-init on import
init_db()
