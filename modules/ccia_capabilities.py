import subprocess
import json
import sqlite3
import sqlite_vec

class CCiAIntegrator:
    """Módulo de extensión para dotar al enjambre con capacidades aisladas y memoria vectorial."""
    
    def __init__(self, db_path="/home/k1/ccia_workspace/university.db"):
        self.db_path = db_path

    def run_in_podman_sandbox(self, script_path, timeout=30):
        """Ejecuta un script en un contenedor aislado Podman sin acceso a red."""
        cmd = [
            "podman", "run", "--rm",
            "-v", f"{script_path}:/app/script.py:ro",
            "--network", "none",
            "--memory", "1g",
            "python:3.12-slim",
            "python3", "/app/script.py"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return res.returncode == 0, res.stdout, res.stderr
        except Exception as e:
            return False, "", str(e)

    def init_vector_store(self):
        """Inicializa soporte para memoria semántica vectorial usando sqlite_vec."""
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bounty_embeddings (
                    issue_id TEXT PRIMARY KEY,
                    embedding float[384]
                );
            """)
        conn.close()

if __name__ == "__main__":
    integrator = CCiAIntegrator()
    print("✅ Módulo CCiA Capability Integrator listo.")


    def fetch_issue_from_forge(self, forge_type, repo, issue_id):
        """Consulta incidencias desde GitHub (gh), GitLab (glab) o Gitea (tea)."""
        cli_map = {
            "github": ["gh", "issue", "view", str(issue_id), "-R", repo, "--json", "title,body"],
            "gitlab": ["glab", "issue", "view", str(issue_id), "-R", repo],
            "gitea": ["tea", "issues", "detail", str(issue_id), "-r", repo]
        }
        cmd = cli_map.get(forge_type.lower())
        if not cmd:
            return False, f"Forja '{forge_type}' no soportada."
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.returncode == 0, res.stdout if res.returncode == 0 else res.stderr
        except Exception as err:
            return False, str(err)


    def generate_ollama_embedding(self, text, model="nomic-embed-text"):
        """Genera vectores de embedding usando la API local de Ollama."""
        import urllib.request
        import json
        url = "http://127.0.0.1:11434/api/embeddings"
        payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res.get("embedding", [])
        except Exception:
            return []
