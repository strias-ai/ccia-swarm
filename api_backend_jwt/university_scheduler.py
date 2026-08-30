# -*- coding: utf-8 -*-
import time
import json
import os
import sys
from datetime import datetime
from study_session import run_immediate_study

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "scheduler_config.json")
PID_FILE = os.path.join(os.path.dirname(__file__), "scheduler.pid")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def is_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        if pid and os.path.exists(f"/proc/{pid}"):
            return int(pid)
    return None

def start_daemon():
    pid = is_running()
    if pid:
        print(f"[!] El demonio de la Universidad ya está activo (PID: {pid}).")
        return
    
    cfg = load_config()
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
        
    try:
        while True:
            run_immediate_study()
            interval = cfg.get("interval_minutes", 60) * 60
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def stop_daemon():
    pid = is_running()
    if pid:
        try:
            os.kill(pid, 15)
            print(f"[+] Formación continua detenida en segundo plano (PID: {pid}).")
        except Exception as e:
            print(f"[-] Error al detener el proceso: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    else:
        print("[!] No hay ningún demonio de formación activo.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--start":
            start_daemon()
        elif arg == "--stop":
            stop_daemon()
        elif arg == "--status":
            pid = is_running()
            if pid:
                print(f"🟢 ACTIVA (PID: {pid})")
            else:
                print("🔴 INACTIVA")
