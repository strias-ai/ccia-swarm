import os
import sqlite3
import subprocess

WORKSPACE = "/home/k1/ccia_workspace"
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🔍 AUDITORÍA DEL DAEMON Y ESTADO DE EJECUCIÓN (ARTEFACTO 63)")
print("=" * 80)

# 1. Comprobar PID y estado en el sistema operativo
print("\n[1/3] VERIFICACIÓN DE PROCESOS ACTIVOS EN SO:")
if os.path.exists(PID_FILE):
    with open(PID_FILE, "r") as f:
        pid_str = f.read().strip()
    print(f"  📌 PID registrado en /tmp/art63_daemon.pid: {pid_str}")
    
    res = subprocess.run(["ps", "-p", pid_str, "-o", "pid,cmd="], capture_output=True, text=True)
    if res.returncode == 0 and pid_str in res.stdout:
        print(f"  🟢 Proceso corriendo en vivo: {res.stdout.strip()}")
    else:
        print(f"  🔴 PROCESO MUERTO: El PID {pid_str} no se encuentra en ejecucion.")
else:
    print("  ⚠️ No existe archivo PID /tmp/art63_daemon.pid.")

# Buscar cualquier otra instancia activa de art_63
ps_art = subprocess.run(["pgrep", "-fa", "art_63.py"], capture_output=True, text=True)
if ps_art.stdout.strip():
    print(f"\n  🔎 Instancias encontradas en ps aux:\n{ps_art.stdout.strip()}")
else:
    print("\n  ❌ Ningún proceso activo de art_63.py en la tabla de procesos del sistema.")

# 2. Inspeccionar archivo de logs
print("\n[2/3] ÚLTIMAS LÍNEAS DE /tmp/art63_reasoning.log:")
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    if lines:
        print("".join(lines[-25:]))
    else:
        print("  ⚠️ El archivo de registro está vacío.")
else:
    print("  ⚠️ El archivo /tmp/art63_reasoning.log no existe aún.")

# 3. Estado de la base de datos
print("\n[3/3] ESTADO DE LA COLA EN BASE DE DATOS (ccia_bounties.db):")
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM bounty_opportunities GROUP BY status")
    counts = c.fetchall()
    for st, cnt in counts:
        print(f"  📊 Estado '{st}': {cnt} tareas")
    
    c.execute("SELECT id, repo, title, status FROM bounty_opportunities WHERE status IN ('PENDING', 'PROCESSING') ORDER BY id ASC LIMIT 3")
    rows = c.fetchall()
    if rows:
        print("\n  📋 Próximos bounties en la cola:")
        for r in rows:
            print(f"     • ID {r[0]} | [{r[3]}] {r[1]} -> {r[2][:60]}")
    conn.close()

print("=" * 80)
