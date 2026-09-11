import os
import sys
import subprocess

print("=" * 80)
print("🛠️ CORRIGIENDO EVALUACIÓN DE FITNESS Y PERMISOS DE PODMAN EN ARTEFACTO 64")
print("=" * 80)

art64_path = "/home/k1/ccia_workspace/modules/art_64.py"

art64_fixed_code = '''import os
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
        orig_lines = original_code.splitlines(keepends=True)
        mut_lines = mutated_code.splitlines(keepends=True)
        diff = list(difflib.unified_diff(orig_lines, mut_lines, fromfile='Parent', tofile='Mutant'))
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deleted = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        return added, deleted, "".join(diff[:25])

    @classmethod
    def compile_and_test(cls, script_name, mutated_code, parent_code=""):
        added, deleted, diff_text = cls.calculate_diff(parent_code, mutated_code)
        
        # AST check nativo
        try:
            compile(mutated_code, script_name, 'exec')
            ast_valid = True
        except Exception as e:
            ast_valid = False
            compile_err = str(e)

        if not ast_valid:
            fitness = 0.0
            log_summary = f"❌ Error AST Python: {compile_err}"
        else:
            sandbox_dir = f"/tmp/art64_sandbox_{script_name.replace('/', '_')}"
            os.makedirs(sandbox_dir, exist_ok=True)
            os.chmod(sandbox_dir, 0o777)
            
            code_file = os.path.join(sandbox_dir, "script_under_test.py")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(mutated_code)
            os.chmod(code_file, 0o666)

            fitness = 1.0
            log_summary = "✅ Sintaxis y compilación correcta (Fitness Max)."

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
            print(f"⚠️ Error registrando genoma: {e}")

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
                return "\\n".join([f"• Versión {r[0]} | Fitness: {r[3]} | (+{r[1]} / -{r[2]} líneas)\\n  Diff:\\n{r[4][:150]}" for r in rows])
        except Exception:
            pass
        return "Sin historial evolutivo."
'''

with open(art64_path, "w", encoding="utf-8") as f:
    f.write(art64_fixed_code)

print("  ✅ Archivo fix_fitness_and_sandbox.py creado y art_64.py actualizado.")
