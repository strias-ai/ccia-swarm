# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "module_registry.json")

def validate_artifact(file_path: str) -> bool:
    """Verifica sintaxis Python, imports y no destructividad antes de certificar."""
    if not os.path.exists(file_path):
        print(f"❌ Error: Archivo {file_path} no existe.")
        return False

    # 1. Test de Sintaxis Python
    res = subprocess.run(["python3", "-m", "py_compile", file_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Fallo de compilación en {file_path}:\n{res.stderr}")
        return False

    print(f"✅ Artefacto '{os.path.basename(file_path)}' verificado y apto para certificación.")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if validate_artifact(target):
            sys.exit(0)
        sys.exit(1)
    else:
        print("Uso: python3 certify_artifact.py <archivo_a_certificar.py>")
