import os
import sys
import json
import sqlite3

print("=" * 80)
print("🛠️ REGISTRANDO ARTEFACTO 64 EN UNIVERSITY.DB (AUTO-INSPECCIÓN DE ESQUEMA)")
print("=" * 80)

db_path = "/home/k1/ccia_workspace/university.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Inspeccionar esquema real de la tabla
    cur.execute("PRAGMA table_info(ccia_artifact_manifests)")
    cols_info = cur.fetchall()
    col_names = [col[1] for col in cols_info]
    not_null_cols = [col[1] for col in cols_info if col[3] == 1]
    
    print(f"  • Columnas detectadas ({len(col_names)}): {', '.join(col_names[:10])}...")
    print(f"  • Campos NOT NULL requeridos: {not_null_cols}")
    
    art64_filepath = "/home/k1/ccia_workspace/modules/art_64.py"
    
    manifest_data = {
        "artifact_id": 64,
        "name": "CCiA Evolutionary Compiler & Genetic Diff Engine",
        "version": "v1.0.0",
        "category": "EVOLUTIONARY_COMPILER",
        "status": "CERTIFIED"
    }
    
    # Map de valores por defecto para evitar fallos NOT NULL
    default_values = {
        "id": 64,
        "artifact_id": 64,
        "artifact_number": 64,
        "name": "CCiA Evolutionary Compiler & Genetic Diff Engine",
        "artifact_name": "CCiA Evolutionary Compiler & Genetic Diff Engine",
        "version": "v1.0.0",
        "category": "EVOLUTIONARY_COMPILER",
        "operational_category": "Auditoría & Calidad",
        "description": "Compilador aislado en Podman con trazabilidad de diffs, calculador de fitness e historial genético.",
        "filepath": art64_filepath,
        "main_script": art64_filepath,
        "script_path": art64_filepath,
        "manifest_json": json.dumps(manifest_data),
        "status": "CERTIFIED",
        "certification_status": "CERTIFIED",
        "created_at": "2026-09-10 00:00:00",
        "updated_at": "2026-09-10 00:00:00"
    }
    
    # Construir objeto de inserción adaptado al esquema detectado
    insert_payload = {}
    for col in col_names:
        if col in default_values:
            insert_payload[col] = default_values[col]
        elif col in not_null_cols:
            insert_payload[col] = "N/A"
            
    fields = ", ".join(insert_payload.keys())
    placeholders = ", ".join(["?"] * len(insert_payload))
    values = tuple(insert_payload.values())
    
    query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({fields}) VALUES ({placeholders})"
    
    try:
        cur.execute(query, values)
        conn.commit()
        print("  ✅ Artefacto 64 registrado correctamente en university.db")
    except Exception as e:
        print(f"  ❌ Error insertando registro: {e}")
    finally:
        conn.close()

print("=" * 80)
