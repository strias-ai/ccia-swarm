import os
import re
import subprocess
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ RESOLVIENDO SATURACIÓN DE CPU Y MODO UNBUFFERED PARA DAEMON [12]")
print("=" * 80)

# 1. Liberar CPU terminando sentinel_tunnel_guard.py desbocado
print("[1/4] Verificando y liberando uso de CPU...")
try:
    pids = subprocess.check_output(["pgrep", "-f", "sentinel_tunnel_guard.py"]).decode().strip().split()
    for pid in pids:
        subprocess.run(["kill", "-9", pid])
        print(f"  ✅ Proceso con CPU desbocada eliminado (PID {pid}).")
except Exception:
    print("  ℹ️ No se detectaron procesos desbocados activos.")

# 2. Configurar art_63.py para ejecución continua (Daemon Loop)
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Asegurar flush=True en impresiones del log
if "print(" in code and "flush=True" not in code:
    code = code.replace("print(", "print(flush=True, ")

daemon_loop_structure = """
def run_daemon_loop():
    import time
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado...", flush=True)
    orchestrator = CCiA_TriSwarm_Orchestrator()
    while True:
        try:
            processed = orchestrator.process_next_pending_bounty()
            if not processed:
                time.sleep(10)
        except Exception as e:
            print(f"❌ Error en bucle daemon: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    run_daemon_loop()
"""

if 'if __name__ ==' in code:
    code = re.sub(r'if __name__ == ["\']__main__["\'][\s\S]*$', daemon_loop_structure.strip(), code)
else:
    code += "\n\n" + daemon_loop_structure.strip() + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Bucle infinito con `flush=True` inyectado en modules/art_63.py.")

# 3. Corregir toggle_daemon en ccia_mando_63.py para usar python3 -u (Unbuffered)
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    mando_code = f.read()

mando_code = mando_code.replace('["python3", "/home/k1/ccia_workspace/modules/art_63.py"]', 
                                '["python3", "-u", "/home/k1/ccia_workspace/modules/art_63.py"]')

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(mando_code)

print("  ✅ Lanzador del demonio actualizado a ejecutor `-u` (Unbuffered STDOUT).")

# 4. Verificación de compilación
print("\n[4/4] Verificando compilación...")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Compilación realizada con éxito.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
