import os
import re
import sqlite3
import subprocess
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🛠️ DESBLOQUEO DEFINITIVO Y EXTRACCIÓN DINÁMICA DE SQLITE PARA EL DAEMON")
print("=" * 80)

# 1. Detener procesos daemon activos y vaciar logs
print("[1/4] Deteniendo instancias atascadas y limpiando temporales...")
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
        os.remove(PID_FILE)
    except Exception:
        pass

# Terminar cualquier subproceso de art_63 en ejecución
pids = subprocess.run(["pgrep", "-f", "art_63.py"], capture_output=True, text=True).stdout.strip().split()
for p in pids:
    if p:
        subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== LOG REINICIADO - DEMONIO CON EXTRACCIÓN DINÁMICA DE SQLITE ===\n")

print("  ✅ Procesos anteriores terminados. /tmp/art63_reasoning.log limpiado.")

# 2. Eliminar referencias hardcodeadas a comment-auto-bot de art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

code = re.sub(r'https://github\.com/karthikabinav/comment-auto-bot/issues/\d+', '', code)
code = re.sub(r'karthikabinav/comment-auto-bot', '', code)

# 3. Inyectar run_daemon_loop con extracción directa desde SQLite
daemon_loop_real = """
def run_daemon_loop():
    import time
    import sqlite3
    
    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado con extracción directa de DB...", flush=True)
    orchestrator = TriSwarmOrchestrator()
    
    while True:
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT id, issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC LIMIT 1")
            row = c.fetchone()
            
            if not row:
                conn.close()
                time.sleep(10)
                continue
                
            task_id, issue_url, repo, title = row[0], row[1], row[2], row[3]
            c.execute("UPDATE bounty_opportunities SET status='PROCESSING' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            
            print(f"\\n🚀 [DAEMON] Procesando Tarea ID {task_id}: {repo} -> {title}", flush=True)
            
            if hasattr(orchestrator, "process_bounty_loop"):
                orchestrator.process_bounty_loop(issue_url=issue_url, repo=repo, title=title)
            elif hasattr(orchestrator, "run_full_pipeline"):
                orchestrator.run_full_pipeline(issue_url=issue_url, repo=repo, title=title)
            elif hasattr(orchestrator, "run_swarm"):
                orchestrator.run_swarm(issue_url=issue_url, repo=repo, title=title)
                
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE bounty_opportunities SET status='COMPLETED' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            print(f"✅ [DAEMON] Tarea ID {task_id} marcada como COMPLETED.\\n", flush=True)
            
        except Exception as e:
            print(f"❌ Error en bucle daemon: {e}", flush=True)
            time.sleep(5)
"""

if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', daemon_loop_real.strip() + "\n\n", code)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Método `run_daemon_loop()` actualizado con extracción secuencial SQLite.")

# 4. Verificación de compilación
print("\n[4/4] Verificando compilación...")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Módulos validados y compilados sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
