import os
import sys
import py_compile
import re
import ast

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ REPARACIÓN DEFINITIVA DE SINTAXIS Y SANGRÍA EN CCIA_MANDO_63.PY")
print("=" * 80)

with open(MANDO_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Definición limpia de la función de conmutación
toggle_func_lines = [
    "import os, sys, subprocess\n",
    "\n",
    "def execute_daemon_toggle_art63():\n",
    "    pid_file = '/tmp/art63_daemon.pid'\n",
    "    log_file = '/tmp/art63_reasoning.log'\n",
    "    res = subprocess.run(['pgrep', '-f', 'modules/art_63.py.*--daemon'], capture_output=True, text=True)\n",
    "    pids = [p for p in res.stdout.strip().split() if p]\n",
    "    if pids:\n",
    "        print('\\n🛑 DETENIENDO DEMONIO ARTEFACTO 63...')\n",
    "        for p in pids:\n",
    "            subprocess.run(['kill', '-9', p], stderr=subprocess.DEVNULL)\n",
    "        if os.path.exists(pid_file):\n",
    "            try:\n",
    "                os.remove(pid_file)\n",
    "            except Exception:\n",
    "                pass\n",
    "        print('✅ Demonio y procesos asociados finalizados limpiamente.')\n",
    "    else:\n",
    "        print('\\n🟢 INICIANDO DEMONIO ARTEFACTO 63...')\n",
    "        with open(log_file, 'a', encoding='utf-8') as f_log:\n",
    "            f_log.write('=== LOG REINICIADO DESDE CENTRO DE MANDO ===\\n')\n",
    "        art63_script = '/home/k1/ccia_workspace/modules/art_63.py'\n",
    "        log_fd = open(log_file, 'a', encoding='utf-8')\n",
    "        proc = subprocess.Popen([sys.executable, '-u', art63_script, '--daemon'], stdout=log_fd, stderr=log_fd)\n",
    "        with open(pid_file, 'w') as pf:\n",
    "            pf.write(str(proc.pid))\n",
    "        print(f'✅ Demonio iniciado correctamente con PID {proc.pid}.')\n",
    "\n"
]

# Filtrar funciones e inyecciones corruptas previas
new_lines = []
skip = False
for line in lines:
    if "def execute_daemon_toggle_art63():" in line:
        skip = True
        continue
    if skip and (line.startswith("def ") or (line.strip() and not line.startswith(" ") and not line.startswith("\t"))):
        skip = False
    if not skip:
        new_lines.append(line)

combined = toggle_func_lines + new_lines

# Reestructurar limpiamente el bloque del menú de la opción '12'
final_lines = []
i = 0
while i < len(combined):
    line = combined[i]
    final_lines.append(line)
    
    if re.search(r'elif\s+[a-zA-Z0-9_]+\s*==\s*[\'"]12[\'"]\s*:', line) or re.search(r'if\s+[a-zA-Z0-9_]+\s*==\s*[\'"]12[\'"]\s*:', line):
        curr_indent = len(line) - len(line.lstrip())
        body_indent = " " * (curr_indent + 4)
        final_lines.append(f"{body_indent}execute_daemon_toggle_art63()\n")
        
        # Omitir sub-bloques mal formados hasta la siguiente rama condicional
        i += 1
        while i < len(combined):
            next_line = combined[i]
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_line.strip() and next_indent <= curr_indent and (
                next_line.strip().startswith("elif") or 
                next_line.strip().startswith("else") or 
                next_line.strip().startswith("if") or 
                next_line.strip().startswith("def")
            ):
                break
            i += 1
        continue
    i += 1

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

# Verificar la integridad sintáctica del archivo
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    src = f.read()

try:
    ast.parse(src)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Archivo ccia_mando_63.py reparado y verificado correctamente por AST.")
except Exception as e:
    print(f"  ❌ Error de sintaxis detectado: {e}")

print("=" * 80)
