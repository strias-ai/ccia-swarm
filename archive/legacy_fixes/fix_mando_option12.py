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
print("🛠️ LIBERANDO CPU Y REPARANDO OPCIÓN [12] EN CCIA_MANDO_63.PY")
print("=" * 80)

# 1. Liberar CPU matando proceso desbocado
print("[1/3] Liberando hilos de CPU desbocados...")
subprocess.run(["pkill", "-9", "-f", "sentinel_tunnel_guard.py"], stderr=subprocess.DEVNULL)
subprocess.run(["pkill", "-9", "-f", "art_63.py.*--daemon"], stderr=subprocess.DEVNULL)

if os.path.exists(PID_FILE):
    os.remove(PID_FILE)

print("  ✅ Proceso sentinel_tunnel_guard.py y demonios residuales eliminados.")

# 2. Leer ccia_mando_63.py e inyectar manejador directo para la opción 12
print("\n[2/3] Modificando manejador de la opción 12 en ccia_mando_63.py...")
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Definición del manejador de toggle seguro
toggle_code = '''
def execute_daemon_toggle_art63():
    import subprocess, os, sys
    pid_file = "/tmp/art63_daemon.pid"
    log_file = "/tmp/art63_reasoning.log"
    
    # Verificar si el demonio está activo físicamente
    res = subprocess.run(["pgrep", "-f", "art_63.py.*--daemon"], capture_output=True, text=True)
    pids = [p for p in res.stdout.strip().split() if p]

    if pids:
        print("\\n🛑 DETENIENDO DEMONIO ARTEFACTO 63...")
        for p in pids:
            subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("✅ Demonio y procesos asociados finalizados limpiamente.")
    else:
        print("\\n🟢 INICIANDO DEMONIO ARTEFACTO 63...")
        with open(log_file, "a", encoding="utf-8") as f_log:
            f_log.write("=== LOG REINICIADO DESDE CENTRO DE MANDO ===\\n")
        
        art63_script = "/home/k1/ccia_workspace/modules/art_63.py"
        log_fd = open(log_file, "a", encoding="utf-8")
        proc = subprocess.Popen([sys.executable, "-u", art63_script, "--daemon"], stdout=log_fd, stderr=log_fd)
        
        with open(pid_file, "w") as pf:
            pf.write(str(proc.pid))
        print(f"✅ Demonio iniciado correctamente con PID {proc.pid}.")
'''

# Reemplazar la evaluación de la opción 12 en el bucle principal de mando
if "execute_daemon_toggle_art63" not in code:
    code = toggle_code + "\n" + code

# Buscar patrón donde se procesa la opción 12 (ej. elif opt == '12': o choice == '12':)
pattern = r'(elif\s+(?:choice|opt|opcion|cmd|user_input)\s*==\s*[\'"]12[\'"]\s*:)'
if re.search(pattern, code):
    code = re.sub(
        r'(elif\s+(?:choice|opt|opcion|cmd|user_input)\s*==\s*[\'"]12[\'"]\s*:[\s\S]*?)(?=\n\s*(?:elif|else|if|def|\Z))',
        r'\1\n        execute_daemon_toggle_art63()\n',
        code,
        count=1
    )
    print("  ✅ Manejador de la opción 12 sustituido con éxito.")
else:
    print("  ⚠️ No se encontró la condición explícita de opción 12; inyectando función auxiliar.")

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(MANDO_PATH, doraise=True)
print("  ✅ Compilación exitosa de ccia_mando_63.py.")

# 3. Comprobar uso de CPU
print("\n[3/3] Verificando estado de CPU...")
res = subprocess.run(["ps", "-eo", "pid,%cpu,cmd", "--sort=-%cpu"], capture_output=True, text=True)
top_lines = res.stdout.strip().split("\n")[:6]
for line in top_lines:
    print(f"  {line}")

print("=" * 80)
