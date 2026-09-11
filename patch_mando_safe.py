import os
import sys
import subprocess
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ APLICANDO PARCHE DE APAGADO SEGURO A CCIA_MANDO_63.PY")
print("=" * 80)

# 1. Limpiar procesos de mando duplicados de la sesión previa
print("[1/2] Limpiando procesos de consola duplicados...")
dup_pids = [1541857, 1547018, 1541501, 1546982]
for pid in dup_pids:
    subprocess.run(["kill", "-9", str(pid)], stderr=subprocess.DEVNULL)
print("  ✅ Instancias duplicadas finalizadas.")

# 2. Inyectar la función toggle_daemon_art63 corregida en ccia_mando_63.py
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    code = f.read()

toggle_logic_fixed = '''def toggle_daemon_art63():
    import subprocess, os, sys
    pid_file = "/tmp/art63_daemon.pid"
    
    # Verificar si hay procesos demonio ejecutándose físicamente
    res = subprocess.run(["pgrep", "-f", "modules/art_63.py.*--daemon"], capture_output=True, text=True)
    running_pids = [p for p in res.stdout.strip().split() if p]

    if running_pids:
        print("\\n🛑 DETENIENDO DEMONIO ARTEFACTO 63...")
        for p in running_pids:
            subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("✅ Demonio y subprocesos eliminados correctamente.")
    else:
        print("\\n🟢 INICIANDO DEMONIO ARTEFACTO 63...")
        log_fd = open("/tmp/art63_reasoning.log", "a", encoding="utf-8")
        art63_script = "/home/k1/ccia_workspace/modules/art_63.py"
        proc = subprocess.Popen([sys.executable, "-u", art63_script, "--daemon"], stdout=log_fd, stderr=log_fd)
        with open(pid_file, "w") as pf:
            pf.write(str(proc.pid))
        print(f"✅ Demonio iniciado con PID {proc.pid}.")
'''

if "def toggle_daemon_art63" in code:
    code = re.sub(r'def toggle_daemon_art63\(\):[\s\S]*?(?=\ndef |\nif __name__|\Z)', toggle_logic_fixed.strip() + "\n\n", code)
    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print("\n[2/2] Actualización de ccia_mando_63.py completada.")
else:
    print("\n⚠️ No se encontró la función 'toggle_daemon_art63' en el archivo.")

py_compile.compile(MANDO_PATH, doraise=True)
print("  ✅ Archivo ccia_mando_63.py compilado sin errores.")
print("=" * 80)
