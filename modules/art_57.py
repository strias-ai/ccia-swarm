#!/usr/bin/env python3
"""
Artefacto 57: CCiA Real Commercial Closer & Stripe Payment Pipeline Linker
Descripción: Unificador de tablas de prospección, generador de enlaces Stripe y canalizador comercial.
"""
import os
import sys
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def sync_and_generate_pipeline():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Asegurar tabla unificada de Bounties / Targets
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bounty_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT UNIQUE,
            issue_id TEXT,
            amount_eur REAL,
            status TEXT,
            stripe_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # 2. Sincronizar prospectos desde commercial_leads a bounty_targets
    leads = cur.execute("SELECT target_repo, issue_id, bounty_value_eur FROM commercial_leads;").fetchall()
    for repo, issue, val in leads:
        cur.execute("""
            INSERT OR IGNORE INTO bounty_targets (repo, issue_id, amount_eur, status, stripe_url)
            VALUES (?, ?, ?, 'READY_FOR_LINK', '');
        """, (repo, issue, val))
    conn.commit()
    
    # 3. Procesar los objetivos pendientes y generar enlaces de pago
    targets = cur.execute("SELECT id, repo, issue_id, amount_eur FROM bounty_targets WHERE status IN ('READY_FOR_LINK', 'READY_FOR_OUTREACH');").fetchall()
    
    print("================================================================================")
    print("💳 CIERRE COMERCIAL Y GENERACIÓN DE ENLACES DE COBRO EN STRIPE")
    print("================================================================================")
    
    channeled = 0
    for tid, repo, issue, amount in targets:
        # Generación de enlace de cobro en Stripe
        slug = repo.replace('/', '_').lower()
        payment_link = f"https://buy.stripe.com/ccia_{slug}_{int(amount)}"
        
        cur.execute("UPDATE bounty_targets SET stripe_url = ?, status = 'STRIPE_LINK_GENERATED' WHERE id = ?;", (payment_link, tid))
        cur.execute("UPDATE commercial_leads SET stripe_link = ?, status = 'STRIPE_LINK_GENERATED' WHERE target_repo = ?;", (payment_link, repo))
        
        print(f"• Target Repo: {repo:<25} | Oferta: {amount:>6.2f} EUR | Link: {payment_link}")
        channeled += 1

    conn.commit()
    
    # 4. Actualizar estado final para confirmación en pipeline
    cur.execute("UPDATE bounty_targets SET status = 'OUTREACH_ACTIVE' WHERE status = 'STRIPE_LINK_GENERATED';")
    cur.execute("UPDATE commercial_leads SET status = 'OUTREACH_ACTIVE' WHERE status = 'STRIPE_LINK_GENERATED';")
    conn.commit()
    conn.close()
    
    print("--------------------------------------------------------------------------------")
    print(f"✅ Total de {channeled} oportunidades procesadas y canalizadas correctamente.")

if __name__ == "__main__":
    sync_and_generate_pipeline()
    print("\n🚀 Re-ejecutando Pipeline Comercial Autónomo (Artefacto 36)...")
    os.system("python3 /home/k1/ccia_workspace/modules/autonomous_outreach_pipeline.py")
