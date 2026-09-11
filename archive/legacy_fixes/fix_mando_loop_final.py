import os
import sys
import py_compile
import ast
import re

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ DIAGNÓSTICO Y REPARACIÓN DEL BUCLE DE MENÚ EN CCIA_MANDO_63.PY")
print("=" * 80)

with open(MANDO_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Definición limpia y desacoplada de la función de conmutación
toggle_func_code = """
import os, sys, subprocess, signal, time

def execute_daemon_toggle_art63():
    pid_file = '/tmp/art63_daemon.pid'
    log_file = '/tmp/art63_reasoning.log'
    res = subprocess.run(['pgrep', '-f', 'art_63.py'], capture_output=True, text=True)
    raw_pids = [p.strip() for p in res.stdout.strip().split() if p.strip()]
    my_pid = str(os.getpid())
    pids = [p for p in raw_pids if p != my_pid]

    if pids or os.path.exists(pid_file):
        print('\\n🛑 DETENIENDO DEMONIO Y PROCESOS DUPLICADOS DE ARTEFACTO 63...')
        subprocess.run(['pkill', '-9', '-f', 'art_63.py'], stderr=subprocess.DEVNULL)
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except Exception:
                pass
        time.sleep(0.5)
        print('✅ Demonio y subprocesos finalizados limpiamente.')
    else:
        print('\\n🟢 INICIANDO DEMONIO ARTEFACTO 63 EN SEGUNDO PLANO (DESACOPLADO)...')
        with open(log_file, 'a', encoding='utf-8') as f_log:
            f_log.write('\\n=== LOG REINICIADO DESDE CENTRO DE MANDO ===\\n')
        art63_script = '/home/k1/ccia_workspace/modules/art_63.py'
        log_fd = open(log_file, 'a', encoding='utf-8')
        proc = subprocess.Popen(
            [sys.executable, '-u', art63_script, '--daemon'],
            stdout=log_fd,
            stderr=log_fd,
            start_new_session=True,
            close_fds=True
        )
        with open(pid_file, 'w') as pf:
            pf.write(str(proc.pid))
        print(f'✅ Demonio desacoplado iniciado correctamente con PID {proc.pid}.')
        print('👉 Usa la opción [8] o [10] para monitorear el razonamiento sin fuga en pantalla.')
"""

# Limpiar definiciones antiguas
content = re.sub(r'def execute_daemon_toggle_art63\(\):[\s\S]*?(?=\ndef |\nif __name__|\Z)', '', content)
content = toggle_func_code.strip() + "\n\n" + content.strip()

# Parchear el bloque de la opción 12 para que conserve el bucle
pattern = r'(\s*)(elif|if)\s+([a-zA-Z0-9_]+)\s*==\s*[\'"]12[\'"]\s*:[\s\S]*?(?=\n\1(?:elif|else|if|def)|$)'

def replacement_block(match):
    indent = match.group(1)
    keyword = match.group(2)
    varname = match.group(3)
    body_indent = indent + "    "
    return (
        f"{indent}{keyword} {varname} == '12':\n"
        f"{body_indent}execute_daemon_toggle_art63()\n"
        f"{body_indent}input('\\n[ Presione ENTER para volver al menú ] ')\n"
    )

if re.search(r'(elif|if)\s+[a-zA-Z0-9_]+\s*==\s*[\'"]12[\'"]\s*:', content):
    content = re.sub(pattern, replacement_block, content, count=1)
    print("  ✅ Bloque de opción [12] parcheado con pausa interactiva y retorno al bucle.")
else:
    print("  ⚠️ No se encontró la condición de opción 12 en el patrón exacto.")

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(content)

# Verificar la validez de la sintaxis
try:
    with open(MANDO_PATH, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ ccia_mando_63.py verificado y compilado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
