# -*- coding: utf-8 -*-
"""
CCIA SQLITE WAL OPTIMIZER v1.0
Fuerza el modo WAL y optimiza índices en university.db para maximizar la concurrencia.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def optimize_database_concurrency() -> str:
    if not os.path.exists(DB_PATH):
        return "⚠️ university.db no encontrada."

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        journal_mode = cur.fetchone()[0]
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA optimize;")
        conn.commit()
        conn.close()
        return f"🗄️ Database WAL Engine: Mode={journal_mode.upper()} | Sync=NORMAL | Indexed=OK"
    except Exception as e:
        return f"🔴 Error SQLite WAL: {e}"

if __name__ == "__main__":
    print(optimize_database_concurrency())
