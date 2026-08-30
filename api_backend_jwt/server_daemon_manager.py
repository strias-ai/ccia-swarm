# -*- coding: utf-8 -*-
import subprocess
import sqlite3
import time

DB_PATH = "/home/k1/ccia_workspace/university.db"

def get_system_daemons_status():
    fastapi = subprocess.call("pgrep -f uvicorn > /dev/null", shell=True) == 0
    docker_vant = subprocess.call("docker ps | grep superccia_vant_container > /dev/null", shell=True) == 0
    cloudflare = subprocess.call("pgrep -f cloudflared > /dev/null", shell=True) == 0
    
    return {
        "fastapi_backend": "RUNNING" if fastapi else "STOPPED",
        "docker_vant": "RUNNING" if docker_vant else "STOPPED",
        "cloudflare_tunnel": "RUNNING" if cloudflare else "STOPPED"
    }

def log_vant_event(agent: str, action: str, status: str, payload: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vant_agent_telemetry (agent_name, action, status, payload) VALUES (?, ?, ?, ?)",
        (agent, action, status, payload)
    )
    conn.commit()
    conn.close()
