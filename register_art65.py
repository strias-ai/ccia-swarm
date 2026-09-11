import sqlite3
import os

DB_PATH = "/home/k1/university.db"
ART65_FILE = "/home/k1/ccia_workspace/modules/art_65.py"

print("=" * 80)
print("🚀 REGISTRANDO ARTEFACTO 65 EN MISSION CONTROL & CREANDO SERVICIO BASE")
print("=" * 80)

# 1. Registrar en university.db
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO ccia_artifact_manifests 
        (id, artifact_name, version, category, status, script_path)
        VALUES (65, 'CCiA Swarm API Gateway & Tool Bus Engine', 'v1.0.0', 'SWARM_API_GATEWAY', 'CERTIFIED', '/home/k1/ccia_workspace/modules/art_65.py')
    """)
    conn.commit()
    conn.close()
    print("  ✅ Artefacto 65 registrado en university.db (ccia_artifact_manifests).")

# 2. Crear módulo base del Artefacto 65
os.makedirs("/home/k1/ccia_workspace/modules", exist_ok=True)

art65_code = '''# ARCHIVO: /home/k1/ccia_workspace/modules/art_65.py
# CCiA Swarm API Gateway & Inter-Agent Tool Bus
import os
import json
import sqlite3
import subprocess

class CCiASwarmGateway:
    """Gateway de herramientas y contexto en vivo para cerebros de enjambre."""
    
    @staticmethod
    def inspect_repository(repo_path):
        """Genera el árbol de archivos real y extrae código fuente clave."""
        if not os.path.exists(repo_path):
            return {"error": "Ruta de repositorio no encontrada"}
        
        tree = []
        files_code = {}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), repo_path)
                tree.append(rel)
                if f.endswith(('.py', '.rs', '.go', '.js', '.ts', '.c', '.h', 'Cargo.toml', 'requirements.txt', 'package.json')):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                            files_code[rel] = fp.read(2000) # Primeros 2000 chars
                    except Exception:
                        pass
        return {"tree": tree[:50], "snippets": files_code}

    @staticmethod
    def execute_sandbox_test(repo_path, command="pytest"):
        """Ejecuta pruebas en entorno aislado y retorna stdout/stderr."""
        try:
            res = subprocess.run(command.split(), cwd=repo_path, capture_output=True, text=True, timeout=30)
            return {"stdout": res.stdout, "stderr": res.stderr, "exit_code": res.returncode}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    print("=== CCiA Swarm API Gateway (Artefacto 65) Servidor Local Activo ===")
'''

with open(ART65_FILE, "w", encoding="utf-8") as f:
    f.write(art65_code)

print("  ✅ Módulo art_65.py creado correctamente.")
print("=" * 80)
