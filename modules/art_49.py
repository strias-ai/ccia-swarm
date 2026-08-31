#!/usr/bin/env python3
"""
CCiA Automated Revenue & Payout Dispersion Engine (Artefacto 49)
Filtro estricto: Únicamente liquidaciones REALES verificadas on-chain/Stripe.
"""
import sqlite3
import os

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_payout_dispersion():
    print("💵 Evaluación de Tesorería Soberana & Stripe Webhooks (MODO PRODUCCIÓN REAL)...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    stripe_events = c.execute("SELECT COUNT(*) FROM processed_stripe_events_v2").fetchone()[0] if 'processed_stripe_events_v2' in tables else 0
    
    if 'revenue_settlements' in tables:
        row_real = c.execute("SELECT COUNT(*), SUM(amount_usd) FROM revenue_settlements WHERE mode='REAL' AND signature_verified=1").fetchone()
        cnt_real = row_real[0] if row_real[0] else 0
        tot_real = row_real[1] if row_real[1] else 0.0
    else:
        cnt_real, tot_real = 0, 0.0
        
    print(f"• Eventos Stripe Registrados (v2 Webhook Real): {stripe_events}")
    print(f"• Liquidaciones Reales Verificadas ({cnt_real} ops): ${tot_real:,.2f} USD")
    
    if cnt_real == 0 or tot_real == 0.0:
        print("ℹ️ No hay fondos REALES verificados pendientes de dispersión en tesorería.")
        print("   (Las simulaciones/benchmarks sintéticos han sido excluidas correctamente de los payouts).")
    else:
        print(f"✅ Dispersión de liquidez real de ${tot_real:,.2f} USD lista para proceso SEPA/Crypto.")
        
    conn.close()

if __name__ == "__main__":
    run_payout_dispersion()
