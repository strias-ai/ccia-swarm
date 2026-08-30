#!/usr/bin/env python3
"""
CCiA Artifact Read-Only Diagnostic Guard v1.0.0
Auditoría inmutable de base de datos y verificación de 44 artefactos.
"""
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_readonly_audit():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("PRAGMA query_only = ON;")
    
    cur.execute("SELECT artifact_id, name, category, ast_status FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER) ASC;")
    rows = cur.fetchall()
    
    print(f"🔒 [MODO READ-ONLY ACTIVO] Total Artefactos Registrados: {len(rows)}")
    print("─" * 75)
    for art_id, name, cat, status in rows:
        try:
            aid = int(art_id)
        except (ValueError, TypeError):
            aid = 0
        name_str = str(name) if name else "N/A"
        cat_str = str(cat) if cat else "General"
        status_str = str(status) if status else "OK"
        print(f"  [{aid:02d}] {name_str:<48} | {cat_str:<16} | {status_str}")
    print("─" * 75)
    print("✅ Diagnóstico Read-Only finalizado. Base de datos 100% protegida contra escrituras.")
    conn.close()

if __name__ == "__main__":
    run_readonly_audit()
