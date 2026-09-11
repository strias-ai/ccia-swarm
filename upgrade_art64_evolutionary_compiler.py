import os
import sys
import json
import sqlite3
import difflib
import subprocess

print("=" * 80)
print("🧬 INSTALANDO ARTEFACTO 64: MOTOR COMPILADOR EVOLUTIVO Y TRAZABILIDAD DE DIFFS")
print("=" * 80)

# 1. Crear BD de Genoma y Árbol de Mutaciones
memory_dir = "/home/k1/ccia_workspace/swarm_memory"
os.makedirs(memory_dir, exist_ok=True)
db_genome_path = os.path.join(memory_dir, "genome_tree.db")

conn = sqlite3.connect(db_genome_path)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS script_lineage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        script_name TEXT,
        version INTEGER,
        parent_version INTEGER,
        lines_added INTEGER,
        lines_deleted INTEGER,
        diff_summary TEXT,
        fitness_score REAL,
        sandbox_log TEXT,
        full_code TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
conn.close()

print(f"  ✅ Base de datos de Genoma y Mutaciones creada en: {db_genome_path}")

# 2. Definición del Módulo Artefacto 64 (Compilador Evolutivo)
art64_code = '''import os
import sys
import json
import sqlite3
import difflib
import subprocess

class Artefact64EvolutionaryCompiler:
    """Artefacto 64: Compilador Aislado, Analizador AST y Rastreador de Mutaciones (Diffs)"""

    DB_GENOME = "/home/k1/ccia_workspace/swarm_memory/genome_tree.db"

    @classmethod
    def calculate_diff(cls, original_code, mutated_code):
        """Calcula exactamente qué líneas se añadieron y borraron entre dos generaciones"""
        orig_lines = original_code.splitlines(keepends=True)
        mut_lines = mutated_code.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(orig_lines, mut_lines, fromfile='Parent', tofile='Mutant'))
        
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deleted = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        diff_text = "".join(diff[:25]) # Primeras 25 líneas de diff para resumen
        
        return added, deleted, diff_text

    @classmethod
    def compile_and_test(cls, script_name, mutated_code, parent_code=""):
        """Compila en Sandbox, mide Fitness y guarda la trazabilidad de la mutación"""
        added, deleted, diff_text = cls.calculate_diff(parent_code, mutated_code)
        
        # 1. Probar en Sandbox Podman aislada
        sandbox_dir = f"/tmp/art64_sandbox_{script_name.replace('/', '_')}"
        os.makedirs(sandbox_dir, exist_ok=True)
        
        code_file = os.path.join(sandbox_dir, "script_under_test.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(mutated_code)

        podman_cmd = [
            "/usr/bin/podman", "run", "--rm",
            "-v", f"{sandbox_dir}:/workspace:Z",
            "-w", "/workspace",
            "python:3.11-slim",
            "sh", "-c", "python3 -m py_compile script_under_test.py 2>&1"
        ]
        
        res = subprocess.run(podman_cmd, capture_output=True, text=True, timeout=20)
        
        # 2. Asignar Puntuación de Salud (Fitness Score)
        if res.returncode == 0:
            fitness = 1.0  # Compilado y válido
            log_summary = "✅ Sintaxis y compilación correcta."
        else:
            fitness = 0.0  # Error de sintaxis/compilación
            log_summary = f"❌ Error de compilación:\\n{res.stdout[:200]}"

        # 3. Guardar en el Árbol Genealógico del Genoma
        try:
            conn = sqlite3.connect(cls.DB_GENOME)
            cur = conn.cursor()
            cur.execute("SELECT MAX(version) FROM script_lineage WHERE script_name=?", (script_name,))
            row = cur.fetchone()
            parent_ver = row[0] if row[0] is not None else 0
            curr_ver = parent_ver + 1

            cur.execute("""
                INSERT INTO script_lineage 
                (script_name, version, parent_version, lines_added, lines_deleted, diff_summary, fitness_score, sandbox_log, full_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (script_name, curr_ver, parent_ver, added, deleted, diff_text, fitness, log_summary, mutated_code))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando genoma: {e}")

        return {
            "version": curr_ver,
            "fitness": fitness,
            "added": added,
            "deleted": deleted,
            "diff": diff_text,
            "log": log_summary
        }

    @classmethod
    def get_lineage_history(cls, script_name):
        """Retorna la historia evolutiva para que el enjambre sepa qué borró y qué escribió antes"""
        try:
            conn = sqlite3.connect(cls.DB_GENOME)
            cur = conn.cursor()
            cur.execute("""
                SELECT version, lines_added, lines_deleted, fitness_score, diff_summary 
                FROM script_lineage WHERE script_name=? ORDER BY version DESC LIMIT 3
            """, (script_name,))
            rows = cur.fetchall()
            conn.close()
            if rows:
                history = []
                for r in rows:
                    history.append(f"• Versión {r[0]} | Fitness: {r[3]} | (+{r[1]} / -{r[2]} líneas)\\n  Diff:\\n{r[4][:150]}")
                return "\\n".join(history)
        except Exception:
            pass
        return "Sin historial evolutivo previo para este script."
'''

# Escribir Artefacto 64 en archivo independiente
art64_path = "/home/k1/ccia_workspace/modules/art_64.py"
with open(art64_path, "w", encoding="utf-8") as f:
    f.write(art64_code)

print(f"  ✅ Módulo Artefacto 64 creado en: {art64_path}")

# 3. Importar Artefacto 64 dentro de Artefacto 63
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(art63_path, "r", encoding="utf-8") as f:
    code63 = f.read()

if "from modules.art_64 import Artefact64EvolutionaryCompiler" not in code63:
    code63 = "from modules.art_64 import Artefact64EvolutionaryCompiler\n" + code63
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(code63)
    print("  ✅ Artefacto 64 vinculado con éxito dentro de Artefacto 63.")

# Compilación de prueba
subprocess.run([sys.executable, "-m", "py_compile", art64_path], check=True)
subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Compilaciones de Artefacto 63 y Artefacto 64 exitosas.")
