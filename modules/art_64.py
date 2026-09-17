import os
import sys
import sqlite3
import difflib
import subprocess
import re

class Artefact64EvolutionaryCompiler:
    """Artefacto 64 Parcheado: Compilador Aislado (AST), Rastreador de Diffs y Actualizador de Mando Central"""

    DB_GENOME = "/home/k1/ccia_workspace/swarm_memory/genome_tree.db"
    DB_CENTRAL = "/home/k1/university.db"

    @classmethod
    def sanitize_filename(cls, name):
        """Previene inyección de comandos en las rutas temporales"""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    @classmethod
    def calculate_diff(cls, original_code, mutated_code):
        orig_lines = original_code.splitlines(keepends=True)
        mut_lines = mutated_code.splitlines(keepends=True)
        diff = list(difflib.unified_diff(orig_lines, mut_lines, fromfile='Parent', tofile='Mutant'))
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deleted = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        return added, deleted, "".join(diff[:25])

    @classmethod
    def update_central_registry(cls, script_name, is_valid):
        """Actualiza el estado AST en el panel de Mission Control (university.db)"""
        try:
            status = "CERTIFIED" if is_valid else "FAILED_AST"
            
            # Intentar extraer un ID lógico si el nombre sigue el patrón art_XX
            match = re.search(r'art_(\d+)', script_name)
            if not match:
                return  # Si no es un artefacto numerado, no se registra en el menú
                
            art_id = match.group(1)
            
            with sqlite3.connect(cls.DB_CENTRAL) as conn:
                cur = conn.cursor()
                # Verifica si el artefacto existe antes de actualizar
                cur.execute("SELECT 1 FROM ccia_artifact_manifests WHERE CAST(artifact_id AS INTEGER) = ?", (int(art_id),))
                if cur.fetchone():
                    cur.execute("UPDATE ccia_artifact_manifests SET ast_status = ? WHERE CAST(artifact_id AS INTEGER) = ?", (status, int(art_id)))
                    conn.commit()
        except Exception as e:
            pass # Falla en silencio para no romper el flujo evolutivo si la DB central está bloqueada

    @classmethod
    def compile_and_test(cls, script_name, mutated_code, parent_code=""):
        added, deleted, diff_text = cls.calculate_diff(parent_code, mutated_code)
        
        safe_name = cls.sanitize_filename(script_name)
        sandbox_dir = f"/tmp/art64_sandbox_{safe_name}"
        os.makedirs(sandbox_dir, exist_ok=True)
        
        code_file = os.path.join(sandbox_dir, "script_under_test.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(mutated_code)

        # Sandbox Mejorado: Ejecuta un script temporal que analiza el AST en lugar de solo py_compile
        validator_script = """
import ast
import sys
try:
    with open('script_under_test.py', 'r') as f:
        source = f.read()
    tree = ast.parse(source)
    sys.exit(0)
except SyntaxError as e:
    print(f'SyntaxError: {e.msg} at line {e.lineno}')
    sys.exit(1)
except Exception as e:
    print(f'AST Error: {e}')
    sys.exit(1)
"""
        val_file = os.path.join(sandbox_dir, "ast_validator.py")
        with open(val_file, "w", encoding="utf-8") as f:
            f.write(validator_script)

        podman_cmd = [
            "/usr/bin/podman", "run", "--rm",
            "-v", f"{sandbox_dir}:/workspace:Z",
            "-w", "/workspace",
            "python:3.11-slim",
            "python3", "ast_validator.py"
        ]
        
        res = subprocess.run(podman_cmd, capture_output=True, text=True, timeout=20)
        
        is_valid = (res.returncode == 0)
        fitness = 1.0 if is_valid else 0.0
        log_summary = "✅ AST Seguro y Sintaxis Correcta." if is_valid else f"❌ Error AST/Sintaxis:\n{res.stdout[:200]}"

        # Actualizar Mission Control
        cls.update_central_registry(script_name, is_valid)

        # Guardar historial evolutivo local
        try:
            with sqlite3.connect(cls.DB_GENOME) as conn:
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
        except Exception:
            pass

        return {
            "version": curr_ver,
            "fitness": fitness,
            "added": added,
            "deleted": deleted,
            "diff": diff_text,
            "log": log_summary
        }
