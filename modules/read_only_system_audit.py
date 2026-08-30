#!/usr/bin/env python3
"""
CCiA Read-Only System & Configuration Inspector v1.0.0
Inspecciona configuraciones, esquemas, claves y telemetría sin escribir datos.
"""

import sqlite3
import os

DB_PATH = "/home/k1/ccia_workspace/university.db"

def mask_secret(s):
    if not s or not isinstance(s, str):
        return "N/A"
    if len(s) <= 8:
        return "****"
    return f"{s[:6]}...{s[-4:]}"

def run_read_only_audit():
    print("==========================================================================")
    print("🔍 DIAGNÓSTICO READ-ONLY Y AUDITORÍA DE CONFIGURACIÓN CCiA")
    print("==========================================================================")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de datos no encontrada en {DB_PATH}")
        return

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()

    # 1. Integridad de SQLite
    cur.execute("PRAGMA quick_check;")
    check_res = cur.fetchone()[0]
    print(f"🗄️ Estado Físico DB (`university.db`): {check_res.upper()}")

    # 2. Conteo de Artefactos Registrados
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ccia_artifact_manifests';")
    if cur.fetchone():
        cur.execute("SELECT COUNT(*) FROM ccia_artifact_manifests;")
        total_artifacts = cur.fetchone()[0]
        print(f"📦 Artefactos Registrados en Manifiesto: {total_artifacts}")

    # 3. Inspección de Credenciales (CIF, Stripe, GitHub)
    print("\n🔑 Inspección de Credenciales y Parámetros en DB:")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_credentials';")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(system_credentials);")
        cols = [c[1] for c in cur.fetchall()]
        cur.execute("SELECT * FROM system_credentials LIMIT 10;")
        rows = cur.fetchall()
        for row in rows:
            masked_row = [mask_secret(str(item)) if any(k in str(item).lower() for k in ["sk_", "pk_", "ghp_", "pat_", "secret", "bearer"]) else item for item in row]
            print(f"   • Registro Credencial: {masked_row}")
    else:
        print("   ℹ️ Tabla system_credentials no detectada.")

    # 4. Estado de Pipeline y Entregas SLA
    print("\n📊 Telemetría de Pipeline y SLA:")
    for table_name in ["ccia_outreach_pipeline", "ccia_sla_fulfillments", "revenue_settlements"]:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if cur.fetchone():
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            print(f"   • Tabla `{table_name}`: {count} registros.")

    conn.close()
    print("==========================================================================\n")

if __name__ == "__main__":
    run_read_only_audit()
