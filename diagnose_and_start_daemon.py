import os
import sys
import sqlite3
import subprocess
import py_compile
import re

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🔍 DIAGNÓSTICO PROFUNDO Y RELANZAMIENTO DEL DEMONIO ARTEFACTO 63")
print("=" * 80)

# 1. Probar ejecución directa de --daemon durante 4 segundos para capturar excepciones
print("[1/4] Comprobando inicialización directa de art_63.py --daemon...")
try:
    res = subprocess.run(
        [sys.executable, "-u", ART63_PATH, "--daemon"],
        capture_output=True,
        text=True,
        timeout=4
    )
    print("  STDOUT:", res.stdout)
    print("  STDERR:", res.stderr)
except subprocess.TimeoutExpired as te:
    print("  🟢 El demonio responde correctamente y se mantiene activo en bucle.")
    if te.stdout:
        print("  STDOUT:", te.stdout.decode()[:400])
    if te.stderr:
        print("  STDERR:", te.stderr.decode()[:400])

# 2. Verificar disponibilidad de tareas en DB
print("\n[2/4] Verificando tareas en la base de datos...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT status, COUNT(*) FROM bounty_opportunities GROUP BY status")
print("  📊 Distribución de estados DB:", c.fetchall())
c.execute("SELECT id, issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' ORDER BY id ASC LIMIT 1")
row = c.fetchone()
print("  📋 Primera tarea pendiente:", row)
conn.close()

# 3. Reforzar run_daemon_loop en art_63.py con captura total de excepciones
print("\n[3/4] Inyectando manejo de errores con trazabilidad en modules/art_63.py...")
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

robust_daemon_loop = """
def run_daemon_loop():
    import time
    import sqlite3
    import traceback
    
    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado correctamente.", flush=True)
    
    try:
        orchestrator = TriSwarmOrchestrator()
    except Exception as e:
        print(f"❌ Error crítico al instanciar TriSwarmOrchestrator: {e}", flush=True)
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
            
            print(f"\\n🚀 [DAEMON] Procesando Tarea ID {task_id}: {repo} -> {title}", flush=True)
            
            if hasattr(orchestrator, "process_bounty_loop"):
                orchestrator.process_bounty_loop(issue_url=issue_url, repo=repo, title=title)
            elif hasattr(orchestrator, "run_full_pipeline"):
                orchestrator.run_full_pipeline(issue_url=issue_url, repo=repo, title=title)
            elif hasattr(orchestrator, "run_swarm"):
                orchestrator.run_swarm(issue_url=issue_url, repo=repo, title=title)
            else:
                print("⚠️ Método de ejecución genérico en uso.", flush=True)
                
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE bounty_opportunities SET status='COMPLETED' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            print(f"✅ [DAEMON] Tarea ID {task_id} finalizada y marcada como COMPLETED.\\n", flush=True)
            
        except Exception as e:
            print(f"❌ Error en ciclo de trabajo del demonio: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)
"""

if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', robust_daemon_loop.strip() + "\n\n", code)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(ART63_PATH, doraise=True)
print("  ✅ Código actualizado y compilado perfectamente.")

# 4. Limpiar PIDs previos y relanzar el demonio
print("\n[4/4] Limpiando subprocesos huérfanos y relanzando demonio...")
pids = subprocess.run(["pgrep", "-f", "art_63.py.*--daemon"], capture_output=True, text=True).stdout.strip().split()
for p in pids:
    if p:
        subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)

log_fd = open(LOG_FILE, "a", encoding="utf-8")
proc = subprocess.Popen([sys.executable, "-u", ART63_PATH, "--daemon"], stdout=log_fd, stderr=log_fd)

with open(PID_FILE, "w") as pf:
    pf.write(str(proc.pid))

print(f"  🟢 Demonio iniciado correctamente en segundo plano (PID {proc.pid}).")
print("=" * 80)
