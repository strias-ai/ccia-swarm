# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
import time
import json

DB_PATH = '/home/k1/ccia_workspace/university.db'
LOG_PATH = '/home/k1/ccia_workspace/logs/payout_dispatcher.log'

def log_message(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(formatted + '\n')

def run_payout_dispatcher():
    log_message("💸 [CCiA Artifact 33] Autonomous Treasury & Agent Payout Dispatcher v1.0.0")
    log_message("──────────────────────────────────────────────────────────────────────────")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS treasury_payouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_agent TEXT,
        share_percentage REAL,
        amount_usd REAL,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cur.execute("SELECT SUM(amount_usd) FROM revenue_settlements WHERE status = 'COMPLETED'")
    res = cur.fetchone()[0]
    total_treasury = res if res else 0.0
    
    # Modelo de distribución de tesorería: 50% Reinversión/Infra, 30% Agentes de Bounties, 20% Fondo de Reserva
    allocations = [
        ("INFRASTRUCTURE_RESERVE_AGENT", 0.50),
        ("BOUNTY_HUNTER_SWARM", 0.30),
        ("EMERGENCY_ESCROW_VAULT", 0.20)
    ]
    
    log_message(f"🏦 Fondo Total Disponible en Tesorería: ${total_treasury:.2f} USD")
    
    for agent, share in allocations:
        payout_amount = total_treasury * share
        cur.execute("""
            INSERT INTO treasury_payouts (recipient_agent, share_percentage, amount_usd, status)
            VALUES (?, ?, ?, ?)
        """, (agent, share * 100, payout_amount, 'DISPATCHED'))
        log_message(f"   • Asignado a {agent} ({share*100:.0f}%): ${payout_amount:.2f} USD [DISPATCHED]")
        
    conn.commit()
    conn.close()
    
    log_message("✅ Distribución de Fondos de Tesorería completada exitosamente.")

if __name__ == '__main__':
    run_payout_dispatcher()
