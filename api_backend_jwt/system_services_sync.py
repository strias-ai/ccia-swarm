# -*- coding: utf-8 -*-
import sqlite3, subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"

def sync_services():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(system_services)")
    cols = [col[1] for col in cursor.fetchall()]
    name_col = "service_name" if "service_name" in cols else ("name" if "name" in cols else cols[0])
    
    api_active = subprocess.run("netstat -tuln | grep :8000", shell=True, capture_output=True).returncode == 0
    cursor.execute(f"UPDATE system_services SET status = ? WHERE {name_col} LIKE '%FastAPI%'", ('RUNNING' if api_active else 'STOPPED',))
    
    docker_active = subprocess.run("docker ps | grep superccia_vant", shell=True, capture_output=True).returncode == 0
    cursor.execute(f"UPDATE system_services SET status = ? WHERE {name_col} LIKE '%Docker%'", ('RUNNING' if docker_active else 'STOPPED',))
    
    conn.commit()
    conn.close()
    return {"fastapi": "RUNNING" if api_active else "STOPPED", "docker": "RUNNING" if docker_active else "STOPPED"}

if __name__ == "__main__":
    print("🔄 Sincronizando estados en system_services:", sync_services())
