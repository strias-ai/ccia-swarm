# -*- coding: utf-8 -*-
"""
Validador de Linaje, Verificador AST y Registrador de Manifiestos Fundacionales.
"""

import sqlite3
import py_compile
import json
import os
import sys
import time

DB_PATH = "/home/k1/ccia_workspace/university.db"

def verify_existing_lineage():
    """Paso 1: Auditoría de linaje previo. Todos los módulos registrados deben estar libres de fallos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT artifact_id, main_script FROM ccia_artifact_manifests WHERE ast_status='CERTIFIED'")
    rows = cursor.fetchall()
    conn.close()

    for art_id, script in rows:
        if os.path.exists(script):
            try:
                py_compile.compile(script, doraise=True)
            except Exception as e:
                print(f"❌ FALLO EN LINAJE PREVIO: El artefacto '{art_id}' en {script} presenta errores: {e}")
                return False
    return True

def certify_and_register(artifact_id, name, version, category, main_script, log_file, db_table, manifest_data):
    """Pasos 2, 3 y 4: Validar Manifiesto JSON, Compilar AST y Registrar en DB."""
    print(f"🔍 Iniciando proceso de Certificación para: [{artifact_id}] {name}...")

    # 1. Verificar linaje
    if not verify_existing_lineage():
        print("⛔ CERTIFICACIÓN ABORTADA: Hay artefactos previos en el CCIA con errores AST.")
        return False

    # 2. Verificar campos obligatorios del manifiesto
    required_fields = ["purpose_why", "objective_what_for", "architecture_how_it_works"]
    for field in required_fields:
        if field not in manifest_data or not manifest_data[field]:
            print(f"❌ FALLO DE MANIFIESTO: El campo obligatorio '{field}' falta o está vacío.")
            return False

    # 3. Validar sintaxis AST del script a registrar
    if not os.path.exists(main_script):
        print(f"❌ FALLO DE ARCHIVO: El script target {main_script} no existe.")
        return False

    try:
        py_compile.compile(main_script, doraise=True)
        print("  ✅ Compilación AST Certificada: Sintaxis 100% válida.")
    except Exception as e:
        print(f"  ❌ FALLO SINTÁCTICO AST: {e}")
        return False

    # 4. Registrar o Actualizar en SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        manifest_str = json.dumps(manifest_data, indent=2, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO ccia_artifact_manifests 
            (artifact_id, name, version, category, main_script, log_file, db_table, ast_status, manifest_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'CERTIFIED', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(artifact_id) DO UPDATE SET
                name=excluded.name,
                version=excluded.version,
                category=excluded.category,
                main_script=excluded.main_script,
                log_file=excluded.log_file,
                db_table=excluded.db_table,
                ast_status='CERTIFIED',
                manifest_json=excluded.manifest_json,
                updated_at=CURRENT_TIMESTAMP
        ''', (artifact_id, name, version, category, main_script, log_file, db_table, manifest_str))
        
        conn.commit()
        conn.close()
        print(f"  🎉 ARTEFACTO REGISTRADO CON ÉXITO: {artifact_id} (v{version}) guardado en university.db.\n")
        return True
    except Exception as e:
        print(f"  ❌ Error al insertar en base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ Motor Certificador CCIA v1.0 Listo.")
