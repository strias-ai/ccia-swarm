# -*- coding: utf-8 -*-
"""
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def generate_yield_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Métricas de Clientes y Créditos
    cursor.execute("SELECT COUNT(*), SUM(credits) FROM api_clients")
    total_clients, total_credits = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM api_clients WHERE credits < 1000")
    active_consumers = cursor.fetchone()[0]

    # Métricas de Telemetría Outbound
    cursor.execute("SELECT COUNT(*) FROM vant_agent_telemetry")
    total_leads = cursor.fetchone()[0]

    # Estimación de Ingresos Proyectados ($0.05 por crédito consumido / $15 por lead)
    estimated_mrr = (total_clients * 15.0) + ((10000 * total_clients - (total_credits or 0)) * 0.05)

    conn.close()

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "infrastructure_status": "ONLINE (Tunnel: Persistent)",
        "monetization_metrics": {
            "total_registered_clients": total_clients,
            "active_consuming_clients": active_consumers,
            "total_credits_in_circulation": total_credits,
            "projected_mrr_usd": round(estimated_mrr, 2)
        },
        "telemetry_metrics": {
            "total_scouted_leads": total_leads,
            "conversion_rate_percent": round((total_clients / total_leads * 100), 2) if total_leads > 0 else 0
        }
    }
    return report

if __name__ == "__main__":
    print(json.dumps(generate_yield_report(), indent=2, ensure_ascii=False))
