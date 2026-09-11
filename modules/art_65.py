# ARCHIVO: /home/k1/ccia_workspace/modules/art_65.py
# CCiA Swarm API Gateway & Inter-Agent Tool Bus
import os
import json
import subprocess

class CCiASwarmGateway:
    """Gateway de herramientas y contexto en vivo para cerebros del enjambre."""

    @staticmethod
    def inspect_repository(repo_path):
        if not repo_path or not os.path.exists(repo_path):
            return {"error": "Ruta de repositorio no válida"}
        
        tree = []
        snippets = {}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), repo_path)
                tree.append(rel)
                if f.endswith(('.py', '.rs', '.go', '.js', '.ts', '.c', '.h', 'Cargo.toml', 'requirements.txt')):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                            snippets[rel] = fp.read(1500)
                    except Exception:
                        pass
        return {"file_tree": tree[:40], "code_snippets": snippets}

if __name__ == '__main__':
    print("=== CCiA Swarm API Gateway (Artefacto 65) Activo ===")
