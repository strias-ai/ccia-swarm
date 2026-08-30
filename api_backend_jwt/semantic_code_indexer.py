# -*- coding: utf-8 -*-
"""
CCIA SEMANTIC CODE INDEXER v1.0
Escanea y genera índices de búsqueda vectorial/semántica para la Biblioteca RAG (Opción 6).
"""
import os
import glob

def index_workspace_code(workspace_path: str = "/home/k1/ccia_workspace"):
    indexed_files = []
    for ext in ("*.py", "*.md", "*.json"):
        for filepath in glob.glob(f"{workspace_path}/**/{ext}", recursive=True):
            if "venv" not in filepath and "__pycache__" not in filepath and ".git" not in filepath:
                indexed_files.append(filepath)
    return len(indexed_files), indexed_files[:5]

if __name__ == "__main__":
    count, samples = index_workspace_code()
    print(f"🧠 Indexados {count} archivos en el workspace. Muestra: {samples}")
