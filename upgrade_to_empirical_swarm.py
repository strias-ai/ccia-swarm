import os
import sys
import json
import subprocess

print("=" * 80)
print("🚀 ELEVANDO SISTEMA: WORKSPACES AISLADOS + DEBATES EMPÍRICOS CON ARTEFACTO 64")
print("=" * 80)

ws_dir = "/home/k1/ccia_workspace"
memory_dir = os.path.join(ws_dir, "swarm_memory")
workspaces_base = os.path.join(memory_dir, "workspaces")

# Listado completo de identidades de cerebros
brain_ids = [
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4", "2.5",
    "3.1", "3.2", "3.3", "3.4", "3.5",
    "Q1", "Q2", "Q3"
]

# 1. Crear directorios de trabajo aislados (Scratchpads)
for b_id in brain_ids:
    b_path = os.path.join(workspaces_base, f"brain_{b_id.replace('.', '_')}")
    os.makedirs(b_path, exist_ok=True)

print(f"  ✅ {len(brain_ids)} Workspaces aislados creados en {workspaces_base}")

# 2. Inyectar Motor Empírico y Detector Anti-Bucles en modules/art_63.py
art63_path = os.path.join(ws_dir, "modules", "art_63.py")
with open(art63_path, "r", encoding="utf-8") as f:
    art63_code = f.read()

empirical_bridge_code = '''
# ==============================================================================
# 🧠⚡ PUENTE EMPÍRICO Y CORTACIRCUITOS ANTI-ALUCINACIÓN (ARTEFACTO 63 + 64)
# ==============================================================================
import re
from modules.art_64 import Artefact64EvolutionaryCompiler

class EmpiricalBrainBridge:
    @staticmethod
    def sanitize_output(text):
        """Detecta y neutraliza bucles de repetición de caracteres"""
        if not text:
            return ""
        # Detectar patrones repetitivos de más de 10 caracteres iguales
        if re.search(r'(.)\1{10,}', text):
            clean_text = re.sub(r'(.)\1{10,}', r'\1[...BUCLE INTERCEPTADO POR CORTACIRCUITOS...]', text)
            return clean_text
        return text

    @staticmethod
    def get_brain_workspace(brain_id):
        b_dir = os.path.join("/home/k1/ccia_workspace/swarm_memory/workspaces", f"brain_{str(brain_id).replace('.', '_')}")
        os.makedirs(b_dir, exist_ok=True)
        return b_dir

    @classmethod
    def execute_in_sandbox(cls, brain_id, script_filename, python_code):
        """Permite a un cerebro probar código en Sandbox durante su debate"""
        w_dir = cls.get_brain_workspace(brain_id)
        local_file = os.path.join(w_dir, script_filename)
        
        with open(local_file, "w", encoding="utf-8") as f:
            f.write(python_code)
            
        # Ejecutar en compilador/sandbox del Artefacto 64
        res = Artefact64EvolutionaryCompiler.compile_and_test(script_filename, python_code)
        return res
'''

if "class EmpiricalBrainBridge:" not in art63_code:
    art63_code = empirical_bridge_code + "\n\n" + art63_code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(art63_code)
    print("  ✅ Puente Empírico y Cortacircuitos inyectados en modules/art_63.py")

subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Módulo art_63.py compilado sin errores.")
print("=" * 80)
