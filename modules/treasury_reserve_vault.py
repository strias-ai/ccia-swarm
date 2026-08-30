#!/usr/bin/env python3
"""
CCiA Artifact 38: Treasury Reserve Vault & Profit Allocator v1.1.0 (Strict Live Mode)
Calcula la tesorería basándose exclusivamente en transacciones reales de Stripe.
"""

import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_profit_allocation():
    print("🏦 [ARTEFACTO 38] Asignando fondos en Tesorería sobre cobros REALES...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Filtrar solo transacciones reales de Stripe (IDs de cargo con prefijo 'ch_')
    total_real_revenue = 0.0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='revenue_settlements';")
    if cur.fetchone():
        cur.execute("""
            SELECT SUM(amount_usd) 
            FROM revenue_settlements 
            WHERE source_event LIKE 'ch_%' OR source_event LIKE 'in_%' OR source_event LIKE 'pi_%';
        """)
        res = cur.fetchone()
        if res and res[0]:
            total_real_revenue = float(res[0])
            
    allocations = [
        ("OPERATIONAL_RESERVE", 0.50),  # 50%
        ("SWARM_REINVESTMENT", 0.30),   # 30%
        ("LIQUID_TREASURY", 0.20)       # 20%
    ]
    
    print(f"  💵 Ingreso Real Verificado en Stripe: ${round(total_real_revenue, 2)} USD")
    for vault_name, ratio in allocations:
        allocated_amt = total_real_revenue * ratio
        cur.execute("""
            INSERT INTO ccia_treasury_vaults (vault_name, balance_usd, allocation_ratio)
            VALUES (?, ?, ?)
            ON CONFLICT(vault_name) DO UPDATE SET
                balance_usd = excluded.balance_usd,
                allocation_ratio = excluded.allocation_ratio,
                updated_at = CURRENT_TIMESTAMP;
        """, (vault_name, round(allocated_amt, 2), ratio))
        print(f"  💰 Bóveda [{vault_name}]: ${round(allocated_amt, 2)} USD ({int(ratio*100)}%)")

    conn.commit()
    conn.close()
    print("✅ Distribución de tesorería real completada.\n")

if __name__ == "__main__":
    run_profit_allocation()
