import os
import sys
import json
import sqlite3
import subprocess

print("=" * 80)
print("🧠 CREANDO DIRECTORIO DE MEMORIA PERSISTENTE Y CORRIGIENDO IMPORTS EN ART 63")
print("=" * 80)

# 1. Crear directorio de memoria persistente en el disco duro
memory_dir = "/home/k1/ccia_workspace/swarm_memory"
os.makedirs(memory_dir, exist_ok=True)
db_memory_path = os.path.join(memory_dir, "swarm_knowledge_base.db")

# Inicializar estructura de tablas de aprendizaje
conn = sqlite3.connect(db_memory_path)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS learned_solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo TEXT,
        issue_title TEXT,
        solution_patch TEXT,
        execution_status TEXT,
        score REAL DEFAULT 1.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS subswarm_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        consensus_text TEXT,
        models_used TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
conn.close()

print(f"  ✅ Directorio de memoria en disco creado: {memory_dir}")
print(f"  ✅ Base de datos de conocimiento a largo plazo lista: {db_memory_path}")

# 2. Corregir imports y actualizar art_63.py
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

# Asegurar importaciones requeridas al inicio del archivo
header_imports = "import os\nimport sys\nimport json\nimport sqlite3\nimport subprocess\nimport time\n\n"

# Definición de la clase de memoria de disco
persistent_memory_class = '''
class SwarmPersistentMemory:
    """Sistema de memoria evolutiva en disco duro (/home/k1/ccia_workspace/swarm_memory)"""
    
    DB_PATH = "/home/k1/ccia_workspace/swarm_memory/swarm_knowledge_base.db"

    @classmethod
    def save_solution(cls, repo, issue_title, patch, status):
        """Guarda un parche probado en la memoria persistente"""
        try:
            conn = sqlite3.connect(cls.DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO learned_solutions (repo, issue_title, solution_patch, execution_status) VALUES (?, ?, ?, ?)",
                (repo, issue_title, patch, status)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando en memoria de disco: {e}")

    @classmethod
    def recall_similar_solutions(cls, repo_keyword):
        """Recupera soluciones pasadas aplicadas a repositorios similares"""
        try:
            conn = sqlite3.connect(cls.DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "SELECT issue_title, solution_patch FROM learned_solutions WHERE repo LIKE ? AND execution_status='PASSED' ORDER BY id DESC LIMIT 3",
                (f"%{repo_keyword}%",)
            )
            rows = cur.fetchall()
            conn.close()
            if rows:
                return "\\n".join([f"• Prior Learned Fix [{r[0]}]: {r[1][:150]}..." for r in rows])
        except Exception:
            pass
        return "No hay antecedentes previos guardados para este tipo de problema."
'''

# Inyectar header e imports al principio si faltan
if not code.startswith("import os"):
    code = header_imports + code

if "class SwarmPersistentMemory:" not in code:
    code = persistent_memory_class + "\n\n" + code

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Módulo modules/art_63.py actualizado con SwarmPersistentMemory e imports globales.")

# Compilación de verificación
subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Compilación exitosa.")
