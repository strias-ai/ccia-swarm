#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Crear la tabla canónica si no existe
    c.execute("""
    CREATE TABLE IF NOT EXISTS bounty_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo TEXT,
        issue_id TEXT,
        title TEXT,
        reward REAL DEFAULT 0.0,
        status TEXT DEFAULT 'PENDING',
        issue_url TEXT UNIQUE,
        source TEXT DEFAULT 'GitHub',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Sincronizar columnas existentes para evitar errores de inconsistencia
    c.execute("PRAGMA table_info(bounty_opportunities);")
    existing_cols = [row[1] for row in c.fetchall()]

    col_map = {
        "repo": "TEXT",
        "issue_id": "TEXT",
        "reward": "REAL DEFAULT 0.0",
        "status": "TEXT DEFAULT 'PENDING'",
        "issue_url": "TEXT",
        "source": "TEXT DEFAULT 'GitHub'"
    }

    for col, dtype in col_map.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE bounty_opportunities ADD COLUMN {col} {dtype};")

    # 3. Purga definitiva de registros spam
    c.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%bounty-plaza%' OR title LIKE '%bounty-plaza%' OR title LIKE '%$999999999%'")

    conn.commit()
    conn.close()
    print("✅ [Paso 1] Esquema de 'bounty_opportunities' estandarizado y purgado.")

if __name__ == '__main__':
    migrate()
