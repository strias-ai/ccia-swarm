# -*- coding: utf-8 -*-
"""
CCIA SELF-HEALING WATCHDOG v1.0
Supervisa el puerto 8090 (Dashboard), la formación continua y la integridad SQLite.
"""
import os
import sys
import time
import sqlite3
import subprocess

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "watchdog.log")

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [WATCHDOG] {msg}"
    print(formatted)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def check_and_repair_dashboard():
    """Audita el servidor Web (8090). Si el proceso cayó, lo re-inicia automáticamente."""
    try:
        res = subprocess.run(["fuser", "8090/tcp"], capture_output=True, text=True)
        if res.returncode != 0:
            log("⚠️ Dashboard Web (Puerto 8090) no responde. Autocuando servicio...")
            subprocess.Popen(
                ["nohup", "uvicorn", "web_dashboard:app", "--host", "0.0.0.0", "--port", "8090"],
                cwd=os.path.dirname(__file__),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log("🟢 Dashboard Web re-lanzado en segundo plano.")
    except Exception as e:
        log(f"🔴 Error auditando Dashboard: {e}")

def check_and_repair_db():
    """Audita la integridad estructural de la base de datos university.db."""
    if not os.path.exists(DB_PATH):
        log("⚠️ university.db no detectada. Creando estructura limpia...")
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA quick_check;")
        res = cur.fetchone()
        conn.close()
        if res and res[0] == "ok":
            log("✅ Integridad SQLite (university.db): CORRECTA")
        else:
            log(f"🚨 Anomalía en DB: {res[0]}")
    except Exception as e:
        log(f"🔴 Error comprobando DB: {e}")

def run_watchdog(single_run=False):
    log("🛡️ Autocuración activa ejecutándose...")
    check_and_repair_dashboard()
    check_and_repair_db()

if __name__ == "__main__":
    single = "--single" in sys.argv
    run_watchdog(single_run=single)
