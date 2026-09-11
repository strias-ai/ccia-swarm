import sqlite3
import os
import sys

print("================================================================================")
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN Y ESTADO DE ARTEFACTO 63 & CCiA")
print("================================================================================")

# 1. Rutas y existencia de archivos principales
print("\n📁 [1] ARCHIVOS Y MÓDULOS DE ARTEFACTO 63:")
paths = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py",
    "/home/k1/ccia_workspace/university.db"
]
for p in paths:
    exists = "✅ Existe" if os.path.exists(p) else "❌ No existe"
    size = f"({os.path.getsize(p)} bytes)" if os.path.exists(p) else ""
    print(f"  • {p} ── {exists} {size}")

# 2. Estado de la Base de Datos university.db
db_path = "/home/k1/ccia_workspace/university.db"
print("\n📊 [2] TABLAS Y REGISTROS EN UNIVERSITY.DB:")
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print(f"  • Total Tablas ({len(tables)}): {', '.join(tables)}")
        
        target_tables = ["bounty_vector_memory", "swarm_debates", "proposal_reviews", "artifacts"]
        for t in target_tables:
            if t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                cnt = cur.fetchone()[0]
                print(f"    - Tabla '{t}': {cnt} filas")
        conn.close()
    except Exception as e:
        print(f"  ⚠️ Error consultando SQLite: {e}")

# 3. Inspección de Instancia y Configuración de Cerebros
print("\n🧠 [3] MAPPING DE MODELOS DE OLLAMA PARA LOS CEREBROS DEL ARTEFACTO 63:")
try:
    sys.path.insert(0, "/home/k1/ccia_workspace")
    from modules.art_63 import TriSwarmOrchestrator
    orch = TriSwarmOrchestrator()
    
    if hasattr(orch, "queen_brains"):
        print("  • Reina (Gobernanza Q1, Q2, Q3):")
        for q in orch.queen_brains:
            name = q.get("name", "N/A")
            model = q.get("model", "N/A")
            print(f"    - {name} ── [{model}]")
            
    if hasattr(orch, "swarms"):
        print("  • Enjambres Operativos:")
        for swarm_name, members in orch.swarms.items():
            print(f"    - Enjambre [{swarm_name}] ({len(members)} miembros):")
            for m in members:
                print(f"      * {m.get('name')} ── [{m.get('model')}]")
except Exception as e:
    print(f"  ⚠️ Error instanciando TriSwarmOrchestrator: {e}")

print("\n================================================================================")
