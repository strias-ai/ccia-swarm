import os
import sys
import sqlite3
import subprocess

print("=" * 80)
print("🛠️ REGISTRANDO ARTEFACTO 64 EN UNIVERSITY.DB Y CORRIGIENDO SYS.PATH EN ART_63")
print("=" * 80)

# 1. Insertar configuración dinámica de sys.path en art_63.py
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

path_fix = """import sys
import os
_ws_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ws_root not in sys.path:
    sys.path.insert(0, _ws_root)
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
"""

if "_ws_root = os.path.abspath" not in code:
    code = path_fix + "\n" + code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("  ✅ Resolución de rutas sys.path inyectada en modules/art_63.py")

# 2. Registrar el Artefacto 64 en university.db (ccia_artifact_manifests)
db_path = "/home/k1/ccia_workspace/university.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(ccia_artifact_manifests)")
    columns = [col[1] for col in cur.fetchall()]
    
    artifact_data = {
        "id": 64,
        "artifact_number": 64,
        "name": "CCiA Evolutionary Compiler & Genetic Diff Engine",
        "artifact_name": "CCiA Evolutionary Compiler & Genetic Diff Engine",
        "version": "v1.0.0",
        "category": "EVOLUTIONARY_COMPILER",
        "operational_category": "Auditoría & Calidad",
        "description": "Compilador aislado en Podman con trazabilidad de diffs, calculador de fitness e historial genético.",
        "filepath": "/home/k1/ccia_workspace/modules/art_64.py",
        "status": "CERTIFIED",
        "certification_status": "CERTIFIED"
    }
    
    valid_cols = [c for c in columns if c in artifact_data]
    col_names = ", ".join(valid_cols)
    placeholders = ", ".join(["?"] * len(valid_cols))
    values = [artifact_data[c] for c in valid_cols]
    
    query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({col_names}) VALUES ({placeholders})"
    cur.execute(query, values)
    conn.commit()
    conn.close()
    print("  ✅ Artefacto 64 registrado en university.db (ccia_artifact_manifests).")

# 3. Verificar compilación sin errores
subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
art64_path = "/home/k1/ccia_workspace/modules/art_64.py"
if os.path.exists(art64_path):
    subprocess.run([sys.executable, "-m", "py_compile", art64_path], check=True)

print("  ✅ Módulos verificados y listos.")
print("=" * 80)
