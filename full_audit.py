import os
import sys
import sqlite3
import time

# Asegurar que Python encuentre los módulos internos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from modules.art_64 import Artefact64EvolutionaryCompiler
except ImportError:
    print("❌ ERROR CRÍTICO: No se pudo importar el Artefacto 64 (Motor Evolutivo).")
    print("Asegúrate de haber inyectado el Artefacto 64 correctamente.")
    sys.exit(1)

DB_PATH = "/home/k1/university.db"

def update_db(art_id, status):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ccia_artifact_manifests SET ast_status = ? WHERE CAST(artifact_id AS INTEGER) = ?", (status, int(art_id)))
            conn.commit()
    except Exception:
        pass

def run_real_audit():
    print("=" * 85)
    print("🛡️  AUDITORÍA PROFUNDA EN CASCADA (MOTOR AST Y SANDBOX PODMAN - ARTEFACTO 64)")
    print("=" * 85)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT artifact_id, name, main_script FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER)")
        artifacts = cursor.fetchall()

    passed = 0
    failed = 0
    missing = 0

    print("Analizando código fuente y evaluando seguridad estructural...\n")
    
    for art_id, name, script_path in artifacts:
        # 1. Resolver ruta real del archivo
        target_path = script_path
        if not target_path or not os.path.isabs(target_path):
            script_filename = target_path if target_path else f"art_{int(art_id):02d}.py"
            # Casos especiales de tu ecosistema:
            if str(art_id) == "63": script_filename = "ccia_mando_63.py"
            elif str(art_id) == "64": script_filename = "art_64.py"
            elif str(art_id) == "65": script_filename = "ccia_mando_65.py"
            
            target_path = os.path.join("/home/k1/ccia_workspace/modules", script_filename)
            if not os.path.exists(target_path):
                target_path = os.path.join("/home/k1/ccia_workspace", script_filename)
                
        # 2. Verificación y Auditoría
        if not os.path.exists(target_path):
            # Último intento estándar
            target_path = os.path.join("/home/k1/ccia_workspace/modules", f"art_{int(art_id)}.py")

        if not os.path.exists(target_path):
            print(f"  [{art_id:>2}] {name[:45]:<45} 🔴 ARCHIVO NO ENCONTRADO")
            missing += 1
            update_db(art_id, "MISSING_FILE")
            continue

        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            
            # ¡La magia ocurre aquí! Usar el sandbox AST real
            res = Artefact64EvolutionaryCompiler.compile_and_test(target_path, code)
            
            if res["fitness"] == 1.0:
                print(f"  [{art_id:>2}] {name[:45]:<45} 🟢 AST CERTIFICADO")
                passed += 1
                update_db(art_id, "CERTIFIED")
            else:
                print(f"  [{art_id:>2}] {name[:45]:<45} 🔴 AST FALLIDO (Inseguro)")
                failed += 1
                update_db(art_id, "FAILED_AST")
        except Exception as e:
            print(f"  [{art_id:>2}] {name[:45]:<45} ⚠️ ERROR DE LECTURA")
            failed += 1
            update_db(art_id, "ERROR_READ")
            
    print("\n" + "=" * 85)
    print(f"📊 RESULTADOS FINALES: {passed} Certificados | {failed} Fallidos/Inseguros | {missing} Faltantes")
    print("✅ university.db actualizada. El menú CCIA Mission Control ahora refleja el estado REAL.")
    print("=" * 85)

if __name__ == "__main__":
    run_real_audit()
