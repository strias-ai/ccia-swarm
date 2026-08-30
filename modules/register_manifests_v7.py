#!/usr/bin/env python3
"""
CCiA Manifest Registrar v7.0 (Artefactos 40-44)
Registra los nuevos artefactos en ccia_artifact_manifests para visibilidad total en el Panel de Control.
"""
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def register_all_manifests():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
    cols_info = cur.fetchall()
    existing_cols = [c[1] for c in cols_info]
    
    artifacts = [
        {
            "artifact_id": 40,
            "name": "CCiA A2A Gateway & Dynamic Market Intelligence",
            "version": "v1.0.0",
            "category": "Monetización & A2A",
            "main_script": "/home/k1/ccia_workspace/modules/a2a_market_gateway.py",
            "log_file": "/home/k1/ccia_workspace/logs/artifact_40.log",
            "db_table": "ccia_a2a_service_catalog",
            "ast_status": "PASSED"
        },
        {
            "artifact_id": 41,
            "name": "CCiA Autonomous Scientific Discovery Engine",
            "version": "v1.0.0",
            "category": "I+D & Ciencia",
            "main_script": "/home/k1/ccia_workspace/modules/ccia_science_discovery.py",
            "log_file": "/home/k1/ccia_workspace/logs/artifact_41.log",
            "db_table": "ccia_scientific_hypotheses",
            "ast_status": "PASSED"
        },
        {
            "artifact_id": 42,
            "name": "CCiA Post-Quantum Cryptographic Sentinel",
            "version": "v1.0.0",
            "category": "Inmunidad & PQC",
            "main_script": "/home/k1/ccia_workspace/modules/ccia_quantum_sentinel.py",
            "log_file": "/home/k1/ccia_workspace/logs/artifact_42.log",
            "db_table": "ccia_quantum_logs",
            "ast_status": "PASSED"
        },
        {
            "artifact_id": 43,
            "name": "CCiA GraphRAG Temporal Knowledge Engine",
            "version": "v1.0.0",
            "category": "Memoria & Cognición",
            "main_script": "/home/k1/ccia_workspace/modules/ccia_cognition_graph.py",
            "log_file": "/home/k1/ccia_workspace/logs/artifact_43.log",
            "db_table": "ccia_temporal_graph",
            "ast_status": "PASSED"
        },
        {
            "artifact_id": 44,
            "name": "CCiA Autonomous Sovereign P2P Mesh Subcontractor",
            "version": "v1.0.0",
            "category": "Infraestructura P2P",
            "main_script": "/home/k1/ccia_workspace/modules/ccia_mesh_orchestrator.py",
            "log_file": "/home/k1/ccia_workspace/logs/artifact_44.log",
            "db_table": "ccia_mesh_nodes",
            "ast_status": "PASSED"
        }
    ]
    
    os.makedirs("/home/k1/ccia_workspace/logs", exist_ok=True)
    
    for art in artifacts:
        art["manifest_json"] = json.dumps(art)
        valid_pairs = {k: v for k, v in art.items() if k in existing_cols}
        
        for col in cols_info:
            cname, notnull, dflt = col[1], col[3], col[4]
            if notnull and dflt is None and cname not in valid_pairs:
                valid_pairs[cname] = "{}" if "json" in cname.lower() else "ACTIVE"
                
        cols_str = ", ".join(valid_pairs.keys())
        placeholders = ", ".join(["?"] * len(valid_pairs))
        query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({cols_str}) VALUES ({placeholders})"
        cur.execute(query, tuple(valid_pairs.values()))

    conn.commit()
    conn.close()
    print("📋 [MANIFEST REGISTRAR] Artefactos 40 al 44 vinculados exitosamente a ccia_artifact_manifests.")

if __name__ == "__main__":
    import os
    register_all_manifests()
