import sqlite3
import os
import glob

DB_PATH = "/home/k1/ccia_workspace/university.db"
WORKSPACE_DIR = "/home/k1/ccia_workspace"
MODULES_DIR = "/home/k1/ccia_workspace/modules"

print("=" * 80)
print("🔍 INSPECCIÓN GENERAL DE ARTEFACTOS Y DIAGNÓSTICO DE INTEGRACIÓN (ART. 65)")
print("=" * 80)

# 1. Consultar artefactos registrados en university.db
print("\n1. 📊 Artefactos registrados en university.db:")
if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT artifact_id, name, version, category, status FROM ccia_artifact_manifests ORDER BY artifact_id ASC")
        rows = cursor.fetchall()
        for r in rows:
            print(f"  • [{r[0]}] {r[1]} | Versión: {r[2]} | Categoría: {r[3]} | Estado: {r[4]}")
        conn.close()
    except Exception as e:
        print(f"  ❌ Error al leer university.db: {e}")
else:
    print(f"  ❌ No se encontró la base de datos en {DB_PATH}")

# 2. Escanear archivos de módulos físicos existentes
print("\n2. 📁 Módulos y scripts detectados en el sistema:")
all_files = glob.glob(f"{WORKSPACE_DIR}/*.py") + glob.glob(f"{MODULES_DIR}/*.py")
detected_artifacts = {}

for fpath in all_files:
    fname = os.path.basename(fpath)
    if "art_" in fname or "ccia_" in fname:
        detected_artifacts[fname] = fpath
        print(f"  ✅ Encontrado: {fname} -> {fpath}")

# 3. Evaluar compatibilidad de enlace con Artefacto 65
print("\n3. 🔗 Análisis de preparación de enlace con Artefacto 65:")
critical_targets = {
    "art_63.py": "Tri-Swarm Bounty Orchestrator (Inyección de Contexto & AST)",
    "art_64.py": "Evolutionary Compiler & Genetic Engine (Validación Sandbox)",
    "art_62.py": "Scientific Pro-Bono Engine & A2A Chat (Bus de Mensajería A2A)",
    "art_43.py": "GraphRAG Knowledge Engine (Consulta de Conocimiento Histórico)",
    "art_47.py": "RAM Memory Graph (Inyección de Memoria Volátil)"
}

for script, desc in critical_targets.items():
    found = any(script in fname for fname in detected_artifacts.keys())
    status = "🟢 LISTO PARA CONECTAR" if found else "🟡 MÓDULO PENDIENTE / EN SUBDIRECTORIO"
    print(f"  • {script:<12} | {desc:<60} | {status}")

print("\n" + "=" * 80)
print("💡 COPIA Y PEGA EL RESULTADO SUPERIOR EN EL CHAT PARA GENERAR LOS CONECTORES")
print("=" * 80)
