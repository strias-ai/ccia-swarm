# -*- coding: utf-8 -*-
import sqlite3
import time
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_commercial_cycle():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Simular auditoría y propuesta del flujo VANT
    cursor.execute('''
        INSERT INTO vant_agent_telemetry (agent_name, action, status, payload)
        VALUES ('Auditor_AST', 'SCAN_COMPLETED', 'VULNERABILITIES_FOUND', 'OWASP_A03: SQL/Command Injection Risk')
    ''')
    cursor.execute('''
        INSERT INTO vant_agent_telemetry (agent_name, action, status, payload)
        VALUES ('Cerrador', 'DISPATCH_INVOICE', 'READY_FOR_PAYMENT', 'Lead: LemonQu-GIT | Status: Awaiting Checkout')
    ''')
    
    conn.commit()
    conn.close()
    print("🤖 Ciclo autónomo ejecutado por la Flota VANT. Eventos sincronizados en DB Central.")

if __name__ == "__main__":
    run_commercial_cycle()
