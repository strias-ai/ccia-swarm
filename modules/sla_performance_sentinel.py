# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
import time
import json
import urllib.request
import urllib.error

DB_PATH = '/home/k1/ccia_workspace/university.db'
LOG_PATH = '/home/k1/ccia_workspace/logs/sla_sentinel.log'

def log_message(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(formatted + '\n')

def run_sla_sentinel():
    log_message("⚡ [CCiA Artifact 35] Swarm SLA & Performance Sentinel v1.0.0")
    log_message("──────────────────────────────────────────────────────────────────────────")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sla_performance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint_target TEXT,
        latency_ms REAL,
        status_code INTEGER,
        sla_compliance TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    targets = [
        ("Core API Root", "http://127.0.0.1:8000/"),
        ("Webhook Listener Root", "http://127.0.0.1:8080/")
    ]
    
    max_allowed_latency_ms = 250.0
    
    for name, url in targets:
        start_time = time.time()
        status_code = 0
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CCiA-SLA-Sentinel/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                status_code = resp.getcode()
        except urllib.error.HTTPError as e:
            status_code = e.code
        except Exception:
            status_code = 500
            
        elapsed_ms = (time.time() - start_time) * 1000.0
        compliance = "PASS" if (status_code in (200, 404) and elapsed_ms <= max_allowed_latency_ms) else "VIOLATION"
        
        cur.execute("""
            INSERT INTO sla_performance_logs (endpoint_target, latency_ms, status_code, sla_compliance)
            VALUES (?, ?, ?, ?)
        """, (name, round(elapsed_ms, 2), status_code, compliance))
        
        log_message(f"   • Endpoint: {name:<25} | Latencia: {elapsed_ms:6.2f} ms | Status: {status_code} | SLA: [{compliance}]")
        
    conn.commit()
    conn.close()
    
    log_message("✅ Auditoría de latencia y cumplimiento SLA completada.")

if __name__ == '__main__':
    run_sla_sentinel()
