import os
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")

print("=" * 80)
print("🛠️ CORRIGIENDO NOMBRE DE CLASE DEL ORQUESTADOR EN ARTEFACTO 63")
print("=" * 80)

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Corregir instanciación de la clase del orquestador
code = code.replace("CCiA_TriSwarm_Orchestrator()", "TriSwarmOrchestrator()")

# 2. Ajustar la llamada dentro de run_daemon_loop para usar el método correcto del orquestador
daemon_correct_loop = """
def run_daemon_loop():
    import time
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado...", flush=True)
    orchestrator = TriSwarmOrchestrator()
    while True:
        try:
            if hasattr(orchestrator, "run_full_pipeline"):
                orchestrator.run_full_pipeline()
            elif hasattr(orchestrator, "process_next_pending_bounty"):
                orchestrator.process_next_pending_bounty()
            else:
                print("⚠️ Método de ejecución no encontrado en TriSwarmOrchestrator", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error en bucle daemon: {e}", flush=True)
            time.sleep(5)
"""

if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', daemon_correct_loop.strip() + "\n\n", code)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ 'CCiA_TriSwarm_Orchestrator' corregido a 'TriSwarmOrchestrator'.")

# 3. Verificar compilación
try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ modules/art_63.py verificado y compila correctamente.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
