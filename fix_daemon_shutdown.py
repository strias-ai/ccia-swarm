import os
import sys
import subprocess
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🧹 ANIQUILANDO PROCESOS HUÉRFANOS Y REPARANDO INTERRUPTOR [12]")
print("=" * 80)

# 1. Matar de forma contundente todos los demonios en ejecución
print("[1/3] Finalizando todos los procesos huérfanos de art_63.py...")
subprocess.run(["pkill", "-9", "-f", "art_63.py"], stderr=subprocess.DEVNULL)
subprocess.run(["pkill", "-9", "-f", "fix_daemon"], stderr=subprocess.DEVNULL)

if os.path.exists(PID_FILE):
    os.remove(PID_FILE)

# Limpiar el log con caracteres corruptos
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== LOG DEPURADO Y REINICIADO POR CHRONOS METAMORPH ===\n")

print("  ✅ Todos los procesos huérfanos han sido exterminados.")

# 2. Patch ccia_mando_63.py para que la opción [12] haga un pkill real
print("\n[2/3] Patching ccia_mando_63.py para forzar parada física del demonio...")
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Reemplazar lógica de apagado en el menú de mando
toggle_logic_fixed = """
def toggle_daemon_art63():
    import subprocess, os, sys
    pid_file = "/tmp/art63_daemon.pid"
    
    # Comprobar si hay procesos reales corriendo
    res = subprocess.run(["pgrep", "-f", "art_63.py.*--daemon"], capture_output=True, text=True)
    running_pids = res.stdout.strip().split()

    if running_pids:
        print("\\n🛑 DETENIENDO DEMONIO ARTEFACTO 63...")
        subprocess.run(["pkill", "-9", "-f", "art_63.py.*--daemon"], stderr=subprocess.DEVNULL)
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("✅ Demonio y subprocesos detenidos correctamente.")
    else:
        print("\\n🟢 INICIANDO DEMONIO ARTEFACTO 63...")
        log_fd = open("/tmp/art63_reasoning.log", "a", encoding="utf-8")
        art63_script = "/home/k1/ccia_workspace/modules/art_63.py"
        proc = subprocess.Popen([sys.executable, "-u", art63_script, "--daemon"], stdout=log_fd, stderr=log_fd)
        with open(pid_file, "w") as pf:
            pf.write(str(proc.pid))
        print(f"✅ Demonio iniciado con PID {proc.pid}.")
"""

if "def toggle_daemon_art63" in code:
    code = re.sub(r'def toggle_daemon_art63\(\):[\s\S]*?(?=\ndef|\nif __name__|\Z)', toggle_daemon_art63_fixed := toggle_logic_fixed.strip() + "\n\n", code)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(MANDO_PATH, doraise=True)
print("  ✅ Centro de mando actualizado y verificado.")

print("\n[3/3] Estado actual de procesos Python:")
subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, text=True)
res = subprocess.run(["pgrep", "-f", "art_63.py"], capture_output=True, text=True)
if not res.stdout.strip():
    print("  🟢 Ningún demonio en ejecución. Sistema limpio.")
else:
    print(f"  ⚠️ PIDs aún activos: {res.stdout.strip()}")

print("=" * 80)
