import os
import sys
import py_compile
import re
import ast

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ REPARACIÓN V2: DESACOPLES Y CONTROL TOTAL DE PROCESOS EN CCIA_MANDO_63.PY")
print("=" * 80)

with open(MANDO_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Nueva versión robusta de la función de control de demonio
toggle_func_lines = [
    "import os, sys, subprocess, signal, time\n",
    "\n",
    "def execute_daemon_toggle_art63():\n",
    "    pid_file = '/tmp/art63_daemon.pid'\n",
    "    log_file = '/tmp/art63_reasoning.log'\n",
    "    res = subprocess.run(['pgrep', '-f', 'art_63.py'], capture_output=True, text=True)\n",
    "    raw_pids = [p.strip() for p in res.stdout.strip().split() if p.strip()]\n",
    "    my_pid = str(os.getpid())\n",
    "    pids = [p for p in raw_pids if p != my_pid]\n",
    "\n",
    "    if pids or os.path.exists(pid_file):\n",
    "        print('\\n🛑 DETENIENDO DEMONIO Y PROCESOS DUPLICADOS DE ARTEFACTO 63...')\n",
    "        subprocess.run(['pkill', '-9', '-f', 'art_63.py'], stderr=subprocess.DEVNULL)\n",
    "        if os.path.exists(pid_file):\n",
    "            try:\n",
    "                os.remove(pid_file)\n",
    "            except Exception:\n",
    "                pass\n",
    "        time.sleep(0.5)\n",
    "        print('✅ Demonio y subprocesos finalizados limpiamente.')\n",
    "    else:\n",
    "        print('\\n🟢 INICIANDO DEMONIO ARTEFACTO 63 EN SEGUNDO PLANO (DESACOPADO)...')\n",
    "        with open(log_file, 'a', encoding='utf-8') as f_log:\n",
    "            f_log.write('\\n=== LOG REINICIADO DESDE CENTRO DE MANDO ===\\n')\n",
    "        art63_script = '/home/k1/ccia_workspace/modules/art_63.py'\n",
    "        log_fd = open(log_file, 'a', encoding='utf-8')\n",
    "        proc = subprocess.Popen(\n",
    "            [sys.executable, '-u', art63_script, '--daemon'],\n",
    "            stdout=log_fd,\n",
    "            stderr=log_fd,\n",
    "            start_new_session=True,\n",
    "            close_fds=True\n",
    "        )\n",
    "        with open(pid_file, 'w') as pf:\n",
    "            pf.write(str(proc.pid))\n",
    "        print(f'✅ Demonio desacoplado iniciado correctamente con PID {proc.pid}.')\n",
    "        print('👉 Usa la opción [8] o [10] para monitorear el razonamiento sin fuga en pantalla.')\n",
    "\n"
]

# Filtrar definiciones viejas de la función
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

# Reestructurar bloque condicional de la opción '12'
final_lines = []
i = 0
while i < len(combined):
    line = combined[i]
    final_lines.append(line)
    
    if re.search(r'elif\s+[a-zA-Z0-9_]+\s*==\s*[\'"]12[\'"]\s*:', line) or re.search(r'if\s+[a-zA-Z0-9_]+\s*==\s*[\'"]12[\'"]\s*:', line):
        curr_indent = len(line) - len(line.lstrip())
        body_indent = " " * (curr_indent + 4)
        final_lines.append(f"{body_indent}execute_daemon_toggle_art63()\n")
        
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

# Validar sintaxis
try:
    with open(MANDO_PATH, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ ccia_mando_63.py actualizado y validado correctamente.")
except Exception as e:
    print(f"  ❌ Error sintáctico detectado: {e}")

print("=" * 80)
