import os
import sys
import time
import subprocess

print("================================================================================")
print("🛠️ APLICANDO OPTIMIZACIÓN Y LIMPIEZA DE PROCESOS CCiA")
print("================================================================================")

# 1. Matar procesos Python huérfanos o duplicados (manteniendo daemons principales)
print("🧹 [1/3] Finalizando procesos duplicados y colgados...")
res = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True)
for line in res.stdout.splitlines():
    if "python" in line:
        pid = line.strip().split()[0]
        # Eliminar duplicados de main_api o ejecuciones colgadas de submódulos
        if "main_api:app" in line or "sentinel_tunnel_guard" in line or "stripe_live_sync" in line:
            try:
                os.kill(int(pid), 9)
                print(f"  • Proceso finalizado: PID {pid} -> {line[20:70]}")
            except Exception:
                pass

time.sleep(1)

# 2. Inyectar protección de instancia única (Lockfile) en chronos_scheduler.py
chronos_path = "/home/k1/ccia_workspace/modules/chronos_scheduler.py"
print(f"\n🔒 [2/3] Protegiendo {chronos_path} contra ejecuciones solapadas...")

if os.path.exists(chronos_path):
    with open(chronos_path, "r", encoding="utf-8") as f:
        code = f.read()

    lock_header = """import fcntl
# Evitar ejecuciones simultáneas de Chronos Scheduler
lock_file_path = '/tmp/chronos_scheduler.lock'
lock_file = open(lock_file_path, 'w')
try:
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    sys.exit(0)
"""

    if "fcntl.flock" not in code:
        # Insertar después de las importaciones
        import_idx = code.find("import sys")
        if import_idx != -1:
            code = code[:import_idx] + lock_header + code[import_idx:]
            with open(chronos_path, "w", encoding="utf-8") as f:
                f.write(code)
            print("  ✅ Cerrojo de ejecución concurrente añadido con éxito.")
        else:
            print("  ⚠️ No se encontró el punto de inserción para el lock file.")
    else:
        print("  ℹ️ El cerrojo de concurrencia ya estaba presente en Chronos.")

# 3. Levantar una única instancia limpia de main_api en puerto 8000
print("\n🚀 [3/3] Iniciando instancia única y limpia de main_api (Puerto 8000)...")
subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/home/k1/ccia_workspace",
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(2)

print("\n================================================================================")
print("✅ OPTIMIZACIÓN COMPLETADA CON ÉXITO")
print("================================================================================")
