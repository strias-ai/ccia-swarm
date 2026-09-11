import os
import sys
import py_compile
import re

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS Y SANGRÍA EN CCIA_MANDO_63.PY")
print("=" * 80)

with open(MANDO_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Eliminar cualquier definición duplicada o malformada de execute_daemon_toggle_art63
content = re.sub(r'def execute_daemon_toggle_art63\(\):[\s\S]*?(?=\ndef |\nif __name__|\Z)', '', content)

# 2. Definición limpia en el nivel superior del módulo
toggle_func = '''
def execute_daemon_toggle_art63():
    import subprocess, os, sys
    pid_file = "/tmp/art63_daemon.pid"
    log_file = "/tmp/art63_reasoning.log"
    
    res = subprocess.run(["pgrep", "-f", "modules/art_63.py.*--daemon"], capture_output=True, text=True)
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

# 3. Inyectar la función al inicio del archivo
content = toggle_func.strip() + "\n\n" + content.strip() + "\n"

# 4. Corregir la llamada en la opción 12 en el bucle del menú
match = re.search(r'elif\s+([a-zA-Z0-9_]+)\s*==\s*[\'"]12[\'"]\s*:', content)
if match:
    var_name = match.group(1)
    pattern = rf'elif\s+{var_name}\s*==\s*[\'"]12[\'"]\s*:[\s\S]*?(?=\n\s*(?:elif|else|if|def|\Z))'
    replacement = f'elif {var_name} == "12":\n        execute_daemon_toggle_art63()'
    content = re.sub(pattern, replacement, content, count=1)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(content)

# 5. Compilar para asegurar sangría válida
try:
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Archivo ccia_mando_63.py corregido y compilado con éxito.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación persistente: {e}")

print("=" * 80)
