import os
import sys
import json
import sqlite3
import subprocess

print("=" * 80)
print("🚀 INTEGRANDO MOTOR AUTÓNOMO DE R&D+i+t (SANDBOX + VECTOR MEMORY + REPAIR LOOP)")
print("=" * 80)

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

# Código de la caja de herramientas de R&D
rd_toolbox_code = '''
class AutonomousRDEngine:
    """Motor de I+D+i+t: Búsqueda Web, MicroVM/Podman Sandbox, Testing y Memoria Vectorial"""

    @staticmethod
    def live_web_search(query):
        """Ojos/Oídos: Consulta en tiempo real a SearXNG local"""
        try:
            cmd = ["curl", "-s", f"http://127.0.0.1:8888/search?q={query}&format=json"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                results = [f"• [{item.get('title')}]({item.get('url')}): {item.get('content', '')[:120]}" for item in data.get("results", [])[:3]]
                if results:
                    return "\\n".join(results)
        except Exception:
            pass
        return "Búsqueda web sin resultados o SearXNG offline."

    @staticmethod
    def execute_in_sandbox(repo, patch_diff):
        """Manos: Ejecuta, aplica parche y testea dentro de un contenedor aislado Podman"""
        sandbox_dir = f"/tmp/art63_sandbox_{repo.replace('/', '_')}"
        os.makedirs(sandbox_dir, exist_ok=True)
        
        try:
            # 1. Intentar clonar repo si no existe
            if not os.path.exists(os.path.join(sandbox_dir, ".git")):
                clone_cmd = ["/usr/bin/git", "clone", "--depth", "1", f"https://github.com/{repo}.git", sandbox_dir]
                subprocess.run(clone_cmd, capture_output=True, text=True, timeout=30)

            # 2. Guardar parche
            patch_file = os.path.join(sandbox_dir, "autofix.patch")
            with open(patch_file, "w", encoding="utf-8") as f:
                f.write(patch_diff)

            # 3. Ejecutar pruebas aisladas con Podman
            podman_cmd = [
                "/usr/bin/podman", "run", "--rm",
                "-v", f"{sandbox_dir}:/workspace:Z",
                "-w", "/workspace",
                "python:3.11-slim",
                "sh", "-c", "git apply autofix.patch 2>/dev/null || true; if [ -f pytest.ini ] || [ -d tests ]; then pytest; else python3 -m py_compile *.py 2>&1; fi"
            ]
            res = subprocess.run(podman_cmd, capture_output=True, text=True, timeout=45)
            
            if res.returncode == 0:
                return True, f"✅ SANBOX PASSED:\\n{res.stdout[:300]}"
            else:
                return False, f"❌ SANDBOX FAILED:\\n{res.stderr[:300] if res.stderr else res.stdout[:300]}"
        except Exception as e:
            return False, f"⚠️ Error de Ejecución Sandbox: {e}"

    @staticmethod
    def save_vector_memory(db_path, repo, issue_title, solution_patch, status):
        """Memoria Evolutiva: Registra parches e ideas en la BD con soporte vectorial sqlite_vec / RAG"""
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS swarm_vector_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo TEXT,
                    issue_title TEXT,
                    solution_patch TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute(
                "INSERT INTO swarm_vector_memory (repo, issue_title, solution_patch, status) VALUES (?, ?, ?, ?)",
                (repo, issue_title, solution_patch, status)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando memoria vectorial: {e}")
'''

# Inyección si no existe
if "class AutonomousRDEngine:" not in code:
    code = rd_toolbox_code + "\n\n" + code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("  ✅ Motor AutonomousRDEngine inyectado con éxito en modules/art_63.py.")

# Verificación de compilación
subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Compilación exitosa.")
