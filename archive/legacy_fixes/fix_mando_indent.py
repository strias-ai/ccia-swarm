import os
import sys
import py_compile
import re

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS Y SANGRÍA EN CCIA_MANDO_63.PY")
print("=" * 80)

# 1. Leer el código fuente
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 2. Definición limpia de la función de toggle al inicio
func_def = """
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
"""

# Remover funciones duplicadas previas
content = re.sub(r'def execute_daemon_toggle_art63\(\):[\s\S]*?(?=\ndef |\nif __name__|\Z)', '', content)
content = func_def.strip() + "\n\n" + content.strip() + "\n"

# 3. Reparar sangrías de bloques elif incompletos
lines = content.splitlines(keepends=True)
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Si detectamos una línea elif...:
    if line.strip().startswith("elif") and line.strip().endswith(":"):
        indent_len = len(line) - len(line.lstrip())
        body_indent = " " * (indent_len + 4)
        
        # Comprobar si la siguiente línea no tiene más sangría que la del elif
        if i + 1 >= len(lines) or len(lines[i+1].strip()) == 0 or (len(lines[i+1]) - len(lines[i+1].lstrip())) <= indent_len:
            if "12" in line:
                fixed_lines.append(f"{body_indent}execute_daemon_toggle_art63()\n")
            else:
                fixed_lines.append(f"{body_indent}pass\n")
    i += 1

final_content = "".join(fixed_lines)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(final_content)

# 4. Validar sintaxis con el compilador de Python
try:
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Archivo ccia_mando_63.py reparado y compilado con éxito.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación: {e}")

print("=" * 80)
