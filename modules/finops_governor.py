# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
import time
import json

DB_PATH = '/home/k1/ccia_workspace/university.db'
LOG_PATH = '/home/k1/ccia_workspace/logs/finops_governor.log'

def log_message(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(formatted + '\n')

def run_finops_governor():
    log_message("📈 [CCiA Artifact 34] Swarm Profitability & FinOps Governor v1.0.0")
    log_message("──────────────────────────────────────────────────────────────────────────")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS finops_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gross_revenue_usd REAL,
        total_payouts_usd REAL,
        infra_cost_est_usd REAL,
        net_profit_usd REAL,
        profit_margin_pct REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cur.execute("SELECT SUM(amount_usd) FROM revenue_settlements WHERE status = 'COMPLETED'")
    res_rev = cur.fetchone()[0]
    gross_rev = res_rev if res_rev else 0.0
    
    cur.execute("SELECT SUM(amount_usd) FROM treasury_payouts WHERE status = 'DISPATCHED'")
    res_pay = cur.fetchone()[0]
    total_payouts = res_pay if res_pay else 0.0
    
    # Estimación de costo de infraestructura (NucBox Host + Tailwind + API credits)
    infra_cost = 45.00
    net_profit = gross_rev - infra_cost
    margin_pct = (net_profit / gross_rev * 100) if gross_rev > 0 else 0.0
    
    cur.execute("""
        INSERT INTO finops_metrics (gross_revenue_usd, total_payouts_usd, infra_cost_est_usd, net_profit_usd, profit_margin_pct)
        VALUES (?, ?, ?, ?, ?)
    """, (gross_rev, total_payouts, infra_cost, net_profit, margin_pct))
    
    conn.commit()
    conn.close()
    
    log_message(f"📊 Telemetría Financiera Global:")
    log_message(f"   • Ingresos Brutos Acumulados: ${gross_rev:.2f} USD")
    log_message(f"   • Fondos Liquidados en Tesorería: ${total_payouts:.2f} USD")
    log_message(f"   • Costos Estimados Infraestructura: ${infra_cost:.2f} USD")
    log_message(f"   • Beneficio Neto Enjambre: ${net_profit:.2f} USD")
    log_message(f"   • Margen de Rentabilidad: {margin_pct:.2f}%")
    log_message("✅ Evaluación FinOps completada y registrada.")

if __name__ == '__main__':
    run_finops_governor()
