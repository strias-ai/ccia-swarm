# -*- coding: utf-8 -*-
"""
"""
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_outbound_campaign():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Introspección dinámica de columnas de vant_agent_telemetry
    cursor.execute("PRAGMA table_info(vant_agent_telemetry)")
    columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM vant_agent_telemetry LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"🚀 [OUTBOUND PUBLISHER v2.2.1] Telemetría leída ({len(rows)} leads procesados):")
    for row in rows:
        record = dict(zip(columns, row))
        target = record.get('repo_name') or record.get('repository') or record.get('target') or record.get('id', 'ID-Lead')
        email = record.get('target_email') or record.get('email') or record.get('contact') or 'contacto@lead.com'
        print(f"  [+] Generando propuesta DevSecOps | Prospecto: {target} | Contacto: {email}")
    return len(rows)

if __name__ == "__main__":
    run_outbound_campaign()
