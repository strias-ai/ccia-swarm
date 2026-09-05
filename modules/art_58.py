#!/usr/bin/env python3
"""
Artefacto 58: CCiA System Deep Audit & Telemetry Diagnostic Engine
Descripción: Auditoría de salud del ecosistema, verificación de DB, módulos y leads.
"""
import os
import sys
import glob
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"
MODULES_DIR = "/home/k1/ccia_workspace/modules"

def run_deep_audit():
    print("================================================================================")
    print("🔍 CCiA INFORME DE DIAGNÓSTICO PROFUNDO Y SALUD DE INTEGRACIÓN")
    print("================================================================================")
    
    # 1. Auditoría de Base de Datos
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    manifest_count = cur.execute("SELECT COUNT(*) FROM ccia_artifact_manifests;").fetchone()[0]
    leads_count = cur.execute("SELECT COUNT(*) FROM commercial_leads;").fetchone()[0] if "commercial_leads" in tables else 0
    targets_count = cur.execute("SELECT COUNT(*) FROM bounty_targets;").fetchone()[0] if "bounty_targets" in tables else 0
    active_outreach = cur.execute("SELECT COUNT(*) FROM bounty_targets WHERE status='OUTREACH_ACTIVE';").fetchone()[0] if "bounty_targets" in tables else 0
    
    # 2. Conteo de Módulos Físicos
    py_files = glob.glob(os.path.join(MODULES_DIR, "*.py"))
    
    # 3. Verificación de Entorno
    env_stripe = "CONFIGURADA" if os.getenv("STRIPE_SECRET_KEY") else "NO DETECTADA EN ENV"
    env_github = "DETECTADO" if os.getenv("GITHUB_TOKEN") else "NO DETECTADO EN ENV"

    print(f"• Estado Base de Datos (university.db): {len(tables)} tablas operativas")
    print(f"• Manifiestos de Artefactos Registrados: {manifest_count}")
    print(f"• Archivos Python en Módulos:          {len(py_files)}")
    print("--------------------------------------------------------------------------------")
    print(f"• Leads Totales Cargados:             {leads_count}")
    print(f"• Objetivos de Monetización (Bounties): {targets_count}")
    print(f"• Oportunidades en Enlace Activo:       {active_outreach}")
    print("--------------------------------------------------------------------------------")
    print(f"• Stripe API Key:                       {env_stripe}")
    print(f"• GitHub API Token:                     {env_github}")
    print("================================================================================")
    
    # Muestra de Enlaces Activos
    if targets_count > 0:
        print("📋 OPORTUNIDADES CANALIZADAS Y LISTAS PARA COBRO:")
        rows = cur.execute("SELECT repo, amount_eur, stripe_url, status FROM bounty_targets;").fetchall()
        for r in rows:
            print(f"  ├─ Repo: {r[0]:<25} | Oferta: {r[1]:>6.2f} EUR | Estado: {r[3]}")
            print(f"  │  Link: {r[2]}")
        print("================================================================================")
        
    conn.close()

if __name__ == "__main__":
    run_deep_audit()
