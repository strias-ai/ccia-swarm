# -*- coding: utf-8 -*-
import sqlite3
import sys

DB_PATH = "/home/k1/ccia_workspace/university.db"

def set_credential(service: str, key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_credentials (
            service TEXT PRIMARY KEY,
            api_key TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    cursor.execute("INSERT OR REPLACE INTO system_credentials (service, api_key, status) VALUES (?, ?, 'ACTIVE')", (service, key))
    conn.commit()
    conn.close()
    print(f"✅ Credencial para [{service}] inyectada con éxito en university.db")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 inject_real_credentials.py <SERVICE_NAME> <API_KEY>")
        print("Ejemplo: python3 inject_real_credentials.py GITHUB_TOKEN ghp_xxxx... ")
        print("Ejemplo: python3 inject_real_credentials.py STRIPE_SECRET_KEY sk_live_xxxx...")
    else:
        set_credential(sys.argv[1], sys.argv[2])
