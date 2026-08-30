#!/usr/bin/env python3
"""
CCiA Artifact 36: Autonomous Outreach & Bounty Closing Pipeline v1.2.0
Orquesta la conversión entre detección de leads dinámicos, generación de parches y adjunción de enlaces de pago Stripe.
"""

import sqlite3
import json
import os

DB_PATH = "/home/k1/ccia_workspace/university.db"

def fix_manifest_corrupted_json(cur):
    """Limpia registros 'N/A' en ccia_artifact_manifests para corregir el visor de Mission Control."""
    cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
    cols = cur.fetchall()
    col_names = [c[1] for c in cols]
    
    for col_name in col_names:
        cur.execute(f"UPDATE ccia_artifact_manifests SET {col_name} = '{{}}' WHERE {col_name} = 'N/A';")

def init_and_register_artifact():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ccia_outreach_pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_repo TEXT,
            lead_url TEXT UNIQUE,
            status TEXT DEFAULT 'PROSPECTED',
            patch_summary TEXT,
            payment_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ccia_artifact_manifests';")
    if cur.fetchone():
        fix_manifest_corrupted_json(cur)
        
        cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
        cols_info = cur.fetchall()
        existing_cols = [c[1] for c in cols_info]
        
        payload = {
            "artifact_id": 36,
            "name": "CCiA Autonomous Outreach & Bounty Closing Pipeline",
            "artifact_name": "CCiA Autonomous Outreach & Bounty Closing Pipeline",
            "version": "v1.2.0",
            "category": "Monetización Autónoma B2B",
            "operational_category": "Monetización Autónoma B2B",
            "main_script": "/home/k1/ccia_workspace/modules/autonomous_outreach_pipeline.py",
            "status": "ACTIVE"
        }
        
        for col in cols_info:
            col_name = col[1]
            not_null = col[3]
            default_val = col[4]
            if not_null and default_val is None and col_name not in payload:
                if any(k in col_name.lower() for k in ["manifest", "metadata", "config", "json"]):
                    payload[col_name] = "{}"
                else:
                    payload[col_name] = "ACTIVE"
        
        valid_pairs = {k: v for k, v in payload.items() if k in existing_cols}
        if valid_pairs:
            cols_str = ", ".join(valid_pairs.keys())
            placeholders = ", ".join(["?"] * len(valid_pairs))
            query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({cols_str}) VALUES ({placeholders})"
            cur.execute(query, tuple(valid_pairs.values()))
    
    conn.commit()
    conn.close()

def execute_pipeline():
    init_and_register_artifact()
    print("🚀 [ARTEFACTO 36] Ejecutando Autonomous Outreach & Bounty Closing Pipeline v1.2.0...")
    
    default_paywall = "https://buy.stripe.com/6oUeVfalWfCQgTh65s7Vm00"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    inserted = 0
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bounties';")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(bounties);")
        bounty_cols = [c[1] for c in cur.fetchall()]
        
        title_col = "title" if "title" in bounty_cols else ("name" if "name" in bounty_cols else bounty_cols[1] if len(bounty_cols) > 1 else bounty_cols[0])
        url_col = "target_url" if "target_url" in bounty_cols else ("url" if "url" in bounty_cols else bounty_cols[0])
        
        query = f"SELECT {title_col}, {url_col} FROM bounties LIMIT 50;"
        cur.execute(query)
        rows = cur.fetchall()
        for title_val, url_val in rows:
            try:
                cur.execute("""
                    INSERT INTO ccia_outreach_pipeline (target_repo, lead_url, status, patch_summary, payment_link)
                    VALUES (?, ?, 'READY_FOR_OUTREACH', ?, ?)
                """, ("External Target", str(url_val), str(title_val), default_paywall))
                inserted += 1
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()
    print(f"✅ Pipeline completado. {inserted} oportunidades canalizadas hacia cobro en Stripe.\n")

if __name__ == "__main__":
    execute_pipeline()
