from __future__ import annotations
import json
import sqlite3
from typing import Any, Dict

DB_PATH = "datacenter_messages.db"

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mqtt_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                topic TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)
        conn.commit()

def store_message(topic: str, payload: Dict[str, Any]) -> None:
    ts = payload.get("ts")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO mqtt_messages (ts, topic, payload_json) VALUES (?, ?, ?)",
            (ts, topic, json.dumps(payload)),
        )
        conn.commit()

