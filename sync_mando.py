import py_compile

def sync_mando_file():
    with open("/home/k1/ccia_workspace/ccia_mando_63.py", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Reemplazar la importación e instanciación para que apunte directamente a TriSwarmOrchestrator
    sync_code = """import sys
import os
sys.path.append("/home/k1/ccia_workspace/modules")
from art_63 import TriSwarmOrchestrator

if __name__ == "__main__":
    orch = TriSwarmOrchestrator()
    orch.run_full_pipeline()
"""
    with open("/home/k1/ccia_workspace/run_pipeline_direct.py", "w", encoding="utf-8") as f:
        f.write(sync_code)

    py_compile.compile("/home/k1/ccia_workspace/modules/art_63.py", doraise=True)
    print("✅ Módulo modules/art_63.py compilado sin errores de sintaxis.")

sync_mando_file()
