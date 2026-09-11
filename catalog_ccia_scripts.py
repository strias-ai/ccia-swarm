import os
import glob
import sqlite3

WORKSPACE_DIR = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE_DIR, "university.db")

# Patrones identificadores de scripts temporales / parcheo / mantenimiento
PATCH_PATTERNS = [
    "patch_", "repair_", "apply_", "clean_", "fix_", "sync_",
    "surgical_", "total_fix_", "rebuild_", "reconstruct_",
    "reset_", "sanitize_", "purge_", "align_", "find_",
    "identify_", "inject_", "locate_", "master_", "finalize_", "certify_"
]

def catalog_system():
    print("=" * 80)
    print("📚 CATALOGADOR Y CLASIFICADOR DE SCRIPTS - SYSTEM CCiA")
    print("=" * 80)
    print("⚠️  Nota: Este script es de SOLO LECTURA. Ningún archivo será movido o alterado.\n")

    # 1. Obtener artefactos registrados en DB si la base de datos existe
    db_artifacts = {}
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Intentar consultar la tabla de manifiestos/artefactos
            cursor.execute("SELECT id, name, file_path FROM artifacts ORDER BY id ASC")
            rows = cursor.fetchall()
            for r in rows:
                db_artifacts[r[0]] = {"name": r[1], "path": r[2]}
            conn.close()
        except Exception as e:
            # Si cambia el esquema o la tabla, capturamos suavemente
            pass

    # 2. Escanear todos los archivos .py en el workspace y subdirectorios
    all_py_files = []
    for root, _, files in os.walk(WORKSPACE_DIR):
        for f in files:
            if f.endswith(".py"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                all_py_files.append((f, rel_path, full_path))

    # Clasificadores
    temp_patch_scripts = []
    utility_scripts = []
    registered_files = set()

    for fname, rel_path, full_path in sorted(all_py_files, key=lambda x: x[1]):
        # Comprobar si pertenece a patrones temporales
        is_patch = any(fname.lower().startswith(prefix) for prefix in PATCH_PATTERNS)
        
        if is_patch:
            temp_patch_scripts.append(rel_path)
        else:
            utility_scripts.append(rel_path)

    # 3. MOSTRAR INFORME CLASIFICADO
    
    # SECCIÓN 1: ARTEFACTOS DB
    print(f"📌 1. ARTEFACTOS OFICIALES REGISTRADOS EN DB ({len(db_artifacts)} Registros):")
    print("-" * 80)
    if db_artifacts:
        for art_id, info in db_artifacts.items():
            print(f"  • [Art {art_id:02d}] {info['name']} -> {info['path']}")
    else:
        print("  (Consultar vía DB Manager / Manifest)")

    # SECCIÓN 2: SCRIPTS DE UTILIDAD, HERRAMIENTAS Y MÓDULOS
    print(f"\n⚙️ 2. SCRIPTS DE UTILIDAD, MÓDULOS Y DASHBOARDS ACTIVOS ({len(utility_scripts)} Archivos):")
    print("-" * 80)
    for script in utility_scripts:
        print(f"  • {script}")

    # SECCIÓN 3: TEMPORALES / PARCHEO / REPARACIÓN
    print(f"\n🛠️ 3. SCRIPTS TEMPORALES, PARCHES Y REPARADORES ({len(temp_patch_scripts)} Archivos):")
    print("-" * 80)
    for script in temp_patch_scripts:
        print(f"  • {script}")

    # RESUMEN
    print("\n" + "=" * 80)
    print("📊 RESUMEN GENERAL DEL WORKSPACE CCiA:")
    print("=" * 80)
    print(f"  • Total de archivos .py encontrados : {len(all_py_files)}")
    print(f"  • Artefactos DB registrados          : {len(db_artifacts)}")
    print(f"  • Scripts de utilidad / Módulos      : {len(utility_scripts)}")
    print(f"  • Scripts de parcheo / Temporales    : {len(temp_patch_scripts)}")
    print("=" * 80)

if __name__ == "__main__":
    catalog_system()
