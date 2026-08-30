#!/usr/bin/env python3
"""
CCiA Artifact 39: Universal Tunnel & Sentinel Guard v1.0.0
Monitoriza puertos internos (8000/8080), servicios Uvicorn/Chronos, integridad SQLite 
y el estado del túnel Tailscale Funnel. Registra telemetría 100% en university.db (Mission Control).
"""

import sqlite3
import subprocess
import socket
import json
import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_sentinel_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Tabla de Alertas Internas para Mission Control
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ccia_system_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT,
            component TEXT,
            message TEXT,
            auto_resolved INTEGER DEFAULT 0
        );
    """)
    
    # Tabla de Telemetría de Salud
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ccia_health_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            health_score INTEGER,
            active_tunnels INTEGER,
            active_services INTEGER,
            status_summary TEXT
        );
    """)

    # Registrar en el Manifiesto de Artefactos (Artefacto 39)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ccia_artifact_manifests';")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
        cols_info = cur.fetchall()
        existing_cols = [c[1] for c in cols_info]
        
        payload = {
            "artifact_id": 39,
            "name": "CCiA Universal Tunnel & Sentinel Guard",
            "artifact_name": "CCiA Universal Tunnel & Sentinel Guard",
            "version": "v1.0.0",
            "category": "Inmunidad & Autorreparación",
            "operational_category": "Inmunidad & Autorreparación",
            "main_script": "/home/k1/ccia_workspace/modules/universal_tunnel_sentinel.py",
            "status": "ACTIVE"
        }
        
        for col in cols_info:
            col_name = col[1]
            not_null = col[3]
            default_val = col[4]
            if not_null and default_val is None and col_name not in payload:
                payload[col_name] = "{}" if any(k in col_name.lower() for k in ["manifest", "json"]) else "ACTIVE"
        
        valid_pairs = {k: v for k, v in payload.items() if k in existing_cols}
        if valid_pairs:
            cols_str = ", ".join(valid_pairs.keys())
            placeholders = ", ".join(["?"] * len(valid_pairs))
            query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({cols_str}) VALUES ({placeholders})"
            cur.execute(query, tuple(valid_pairs.values()))

    conn.commit()
    conn.close()

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_tailscale_funnel():
    try:
        res = subprocess.run(["tailscale", "funnel", "status"], capture_output=True, text=True, timeout=5)
        if "Funnel on" in res.stdout or "tail01b79c.ts.net" in res.stdout:
            return True, "Funnel Active (https://k1-nucbox-k11.tail01b79c.ts.net -> :8080)"
        return False, "Funnel Offline"
    except Exception as e:
        return False, str(e)

def run_sentinel_audit():
    init_sentinel_tables()
    print("🛡️ [ARTEFACTO 39] Ejecutando Auditoría Sentinel & Diagnóstico de Túneles...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    health_score = 100
    active_services = 0
    active_tunnels = 0
    issues = []
    
    # 1. Verificar Puerto 8000 (Main API)
    if check_port(8000):
        active_services += 1
        print("  ✅ API Core (Puerto 8000): ONLINE")
    else:
        health_score -= 25
        issues.append("API Core en puerto 8000 OFF")
        cur.execute("INSERT INTO ccia_system_alerts (severity, component, message) VALUES ('WARNING', 'API_8000', 'Puerto 8000 inalcanzable')")

    # 2. Verificar Puerto 8080 (Webhook Listener)
    if check_port(8080):
        active_services += 1
        print("  ✅ Webhook Listener (Puerto 8080): ONLINE")
    else:
        health_score -= 30
        issues.append("Webhook Listener en puerto 8080 OFF")
        cur.execute("INSERT INTO ccia_system_alerts (severity, component, message) VALUES ('CRITICAL', 'WEBHOOK_8080', 'Puerto 8080 inalcanzable')")

    # 3. Verificar Tailscale Funnel
    funnel_ok, funnel_msg = check_tailscale_funnel()
    if funnel_ok:
        active_tunnels += 1
        print(f"  ✅ Tailscale Funnel: ONLINE ({funnel_msg})")
    else:
        health_score -= 25
        issues.append("Tailscale Funnel Inactivo")
        cur.execute("INSERT INTO ccia_system_alerts (severity, component, message) VALUES ('CRITICAL', 'TAILSCALE_FUNNEL', ?)", (funnel_msg,))
        # Intentar autorreparación automática de Funnel
        try:
            subprocess.Popen(["tailscale", "funnel", "8080"])
            print("  🔄 [AUTO-HEALING] Comando 'tailscale funnel 8080' re-enviado.")
        except Exception:
            pass

    # 4. Verificar Integridad DB SQLite
    try:
        cur.execute("PRAGMA quick_check;")
        res = cur.fetchone()
        if res and res[0] == "ok":
            print("  ✅ Base de Datos (university.db): INTEGRIDAD OK")
        else:
            health_score -= 20
            cur.execute("INSERT INTO ccia_system_alerts (severity, component, message) VALUES ('CRITICAL', 'SQLITE_DB', 'Fallo de integridad en DB')")
    except Exception as e:
        health_score -= 20

    summary = "System Nominal" if health_score == 100 else f"Issues: {', '.join(issues)}"
    
    cur.execute("""
        INSERT INTO ccia_health_telemetry (health_score, active_tunnels, active_services, status_summary)
        VALUES (?, ?, ?, ?);
    """, (health_score, active_tunnels, active_services, summary))
    
    conn.commit()
    conn.close()
    
    print(f"📊 Telemetría Sentinel: Health Score {health_score}/100 | Servicios: {active_services} | Túneles: {active_tunnels}")
    print("✅ Registro de alertas de Sentinel completado en Mission Control.\n")

if __name__ == "__main__":
    run_sentinel_audit()
