#!/usr/bin/env python3
"""
Artefacto 54: CCiA Mission Control Certifier & Dynamic Navigator Engine
Descripción: Certificador AST, normalizador de rutas y central de navegación cruzada para CCiA.
"""
import os
import sys
import ast
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"
MODULES_DIR = "/home/k1/ccia_workspace/modules"
MISSION_CONTROL_PATH = "/home/k1/ccia_mission_control.py"

def audit_ast_syntax(filepath):
    if not os.path.exists(filepath):
        return False, "Archivo no encontrado en disco"
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            ast.parse(f.read(), filename=filepath)
        return True, "AST Sintaxis OK"
    except SyntaxError as se:
        return False, f"SyntaxError L{se.lineno}: {se.msg}"
    except Exception as e:
        return False, f"Error AST: {str(e)}"

def get_artifacts_matrix():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT artifact_id, name, version, category, ast_status, main_script FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER);").fetchall()
    conn.close()
    
    matrix = []
    for r in rows:
        art_id, name, ver, cat, status, raw_script = r
        raw_script = raw_script if raw_script else ""
        
        script_name = os.path.basename(raw_script) if raw_script else f"art_{int(art_id):02d}.py"
        
        if script_name == "ccia_mission_control.py":
            abs_path = MISSION_CONTROL_PATH
        else:
            abs_path = os.path.join(MODULES_DIR, script_name)
            if not os.path.exists(abs_path):
                alt_path = os.path.join(MODULES_DIR, f"art_{int(art_id)}.py")
                if os.path.exists(alt_path):
                    abs_path = alt_path
                    script_name = f"art_{int(art_id)}.py"
                
        exists = os.path.exists(abs_path)
        ast_ok, ast_msg = audit_ast_syntax(abs_path) if exists else (False, "Archivo no existe")
        
        matrix.append({
            "id": int(art_id),
            "name": name,
            "version": ver,
            "category": cat,
            "script_name": script_name,
            "abs_path": abs_path,
            "exists": exists,
            "ast_ok": ast_ok,
            "ast_msg": ast_msg
        })
    return matrix

def show_copyable_summary():
    matrix = get_artifacts_matrix()
    print("\n" + "="*85)
    print("📋 COPIA Y PEGA ESTE BLOQUE EN EL CHAT DE DIAGNÓSTICO:")
    print("="*85)
    for m in matrix:
        status_str = "VALIDATED" if (m["exists"] and m["ast_ok"]) else "FAIL"
        print(f"ID: {m['id']:<3} | Script: {m['script_name']:<32} | Path: {m['abs_path']:<55} | Status: {status_str}")
    print("="*85 + "\n")
    input("[Presiona ENTER para volver al menú...]")

def launch_direct_c2(art_id):
    if not art_id.isdigit():
        print(f"\n❌ Debe ingresar un número de ID válido.")
        input("[Presiona ENTER para continuar...]")
        return

    matrix = get_artifacts_matrix()
    target = next((item for item in matrix if item["id"] == int(art_id)), None)
    if not target:
        print(f"\n❌ Artefacto [{art_id}] no encontrado en el manifiesto.")
        input("[Presiona ENTER para continuar...]")
        return
    
    print(f"\n🚀 Lanzando Mando y Control Directo para Artefacto [{target['id']:02d}] ({target['script_name']})...\n")
    if target["exists"]:
        os.system(f"python3 {target['abs_path']}")
    else:
        print(f"❌ El archivo del módulo no existe en disco: {target['abs_path']}")
    input("\n[Presiona ENTER para volver al Artefacto 54...]")

def display_menu():
    while True:
        os.system("clear")
        print("================================================================================")
        print("🛡️ CCiA MISSION CONTROL CERTIFIER & NAVIGATOR (ARTEFACTO 54)")
        print("================================================================================")
        print("  [1] 🔍 Ver Mapa Completo de Módulos (Nombres, Rutas Absolutas y Estado AST)")
        print("  [2] 🚀 Saltador Directo a Centros de Mando y Control (C2) de Módulos")
        print("  [3] 📋 Generar Resumen Copiable para Inspección en Chat")
        print("  [4] ⚙️ Certificar AST & Reparar Manifiestos de Rutas en university.db")
        print("  [0] ⬅️ Salir")
        
        choice = input("\nCCIA-v19.0 (Artefacto 54)> ").strip()
        
        if choice == "1":
            os.system("clear")
            print("================================================================================")
            print("🗺️ MAPA DE MÓDULOS REGISTRADOS Y RUTAS EN DISCO")
            print("================================================================================")
            matrix = get_artifacts_matrix()
            for m in matrix:
                st = "✅ OK" if (m["exists"] and m["ast_ok"]) else "❌ FAIL"
                print(f"Artefacto [{m['id']:02d}] - {m['name']}")
                print(f"  • Script C2:     {m['script_name']}")
                print(f"  • Ruta Absoluta: {m['abs_path']}")
                print(f"  • Diagnóstico:   {st} ({m['ast_msg']})\n")
            input("[Presiona ENTER para continuar...]")
        elif choice == "2":
            target_id = input("\nIngresa el ID del Artefacto al que deseas saltar (ej: 45, 46, 48, 53): ").strip()
            launch_direct_c2(target_id)
        elif choice == "3":
            show_copyable_summary()
        elif choice == "4":
            print("\n🔄 Certificando sintaxis AST y normalizando rutas en university.db...")
            matrix = get_artifacts_matrix()
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            updated_count = 0
            for m in matrix:
                if m["exists"] and m["ast_ok"]:
                    cur.execute("UPDATE ccia_artifact_manifests SET main_script = ?, ast_status = 'VALIDATED' WHERE CAST(artifact_id AS INTEGER) = ?;", (m["script_name"], m["id"]))
                    updated_count += 1
            conn.commit()
            conn.close()
            print(f"✅ {updated_count} manifiestos normalizados y certificados en la base de datos.")
            input("[Presiona ENTER para continuar...]")
        elif choice == "0":
            break

if __name__ == "__main__":
    display_menu()
