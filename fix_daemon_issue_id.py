import os
import sys
import sqlite3
import subprocess
import py_compile
import re

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🛠️ CORRIGIENDO MAPEO DE issue_id Y RESETEANDO TAREAS EN DB")
print("=" * 80)

# 1. Resetear tareas en estado PROCESSING a PENDING
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE bounty_opportunities SET status='PENDING' WHERE status='PROCESSING'")
conn.commit()
conn.close()
print("  ✅ Tareas en estado PROCESSING reseteadas a PENDING.")

# 2. Detener procesos daemon previos y limpiar temporales
pids = subprocess.run(["pgrep", "-f", "art_63.py.*--daemon"], capture_output=True, text=True).stdout.strip().split()
for p in pids:
    if p:
        subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)

if os.path.exists(PID_FILE):
    os.remove(PID_FILE)

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== LOG INICIADO - DEMONIO CON MAPEO DE ISSUE_ID CORREGIDO ===\n")

# 3. Leer código fuente
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Código autónomo con extracción directa de issue_id (usando raw string)
daemon_loop_fixed = r'''def run_daemon_loop():
    import time
    import sqlite3
    import traceback
    import re
    import inspect

    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado correctamente con issue_id.", flush=True)

    try:
        orchestrator = TriSwarmOrchestrator()
    except Exception as e:
        print(f"❌ Error al instanciar TriSwarmOrchestrator: {e}", flush=True)
        traceback.print_exc()
        return

    while True:
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT id, issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC LIMIT 1")
            row = c.fetchone()

            if not row:
                conn.close()
                time.sleep(5)
                continue

            task_id, issue_url, repo, title = row[0], row[1], row[2], row[3]
            c.execute("UPDATE bounty_opportunities SET status='PROCESSING' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()

            # Extraer issue_id desde la URL (ej. /issues/773 -> "773")
            issue_id = str(task_id)
            if issue_url:
                match = re.search(r'/(?:issues|pull)/(\d+)', str(issue_url))
                if match:
                    issue_id = match.group(1)

            print("", flush=True)
            print(f"🚀 [DAEMON] Procesando Tarea ID {task_id} (Issue #{issue_id}): {repo} -> {title}", flush=True)

            if hasattr(orchestrator, "process_bounty_loop"):
                sig = inspect.signature(orchestrator.process_bounty_loop)
                params = list(sig.parameters.keys())
                
                kwargs = {}
                if "repo" in params:
                    kwargs["repo"] = repo
                if "issue_id" in params:
                    kwargs["issue_id"] = issue_id
                elif "issue_url" in params:
                    kwargs["issue_url"] = issue_url
                if "title" in params:
                    kwargs["title"] = title

                orchestrator.process_bounty_loop(**kwargs)
            else:
                print("⚠️ El método process_bounty_loop no está disponible en TriSwarmOrchestrator.", flush=True)

            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE bounty_opportunities SET status='COMPLETED' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            print(f"✅ [DAEMON] Tarea ID {task_id} finalizada y marcada como COMPLETED.", flush=True)
            print("", flush=True)

        except Exception as e:
            print(f"❌ Error en ciclo de trabajo del demonio: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)'''

# Reemplazo seguro mediante truncado del bloque previo o sustitución mediante lambda
if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', lambda m: daemon_loop_fixed + "\n\n", code)
else:
    code = code.strip() + "\n\n" + daemon_loop_fixed + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(ART63_PATH, doraise=True)
print("  ✅ Módulo modules/art_63.py actualizado y compilado correctamente.")

# 4. Arrancar proceso daemon en segundo plano
log_fd = open(LOG_FILE, "a", encoding="utf-8")
proc = subprocess.Popen([sys.executable, "-u", ART63_PATH, "--daemon"], stdout=log_fd, stderr=log_fd)

with open(PID_FILE, "w") as pf:
    pf.write(str(proc.pid))

print(f"  🟢 Demonio iniciado correctamente con PID {proc.pid}.")
print("=" * 80)
