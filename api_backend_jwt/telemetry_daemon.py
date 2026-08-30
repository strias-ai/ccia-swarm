# -*- coding: utf-8 -*-
import time
import sqlite3
import psutil
import urllib.request
import json
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "telemetry.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_usage REAL,
            ram_usage REAL,
            ram_available_mb REAL,
            ollama_status TEXT
        )
    """)
    conn.commit()
    conn.close()

def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                models = [m['name'] for m in data.get('models', [])]
                return f"online ({len(models)} modelos)"
    except Exception:
        return "offline"
    return "unknown"

def collect_metrics():
    init_db()
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ollama = check_ollama()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO metrics (cpu_usage, ram_usage, ram_available_mb, ollama_status) VALUES (?, ?, ?, ?)",
        (cpu, ram.percent, ram.available / (1024 * 1024), ollama)
    )
    conn.commit()
    conn.close()
    return {"cpu": cpu, "ram": ram.percent, "ram_available_mb": round(ram.available / (1024 * 1024), 2), "ollama": ollama}

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        print("[Telemetría] Iniciando demonio continuo (intervalo: 15s)...")
        while True:
            m = collect_metrics()
            print(f"[Telemetría] CPU: {m['cpu']}% | RAM: {m['ram']}% | Ollama: {m['ollama']}")
            time.sleep(15)
    else:
        collect_metrics()
