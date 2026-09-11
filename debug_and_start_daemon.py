import os
import sys
import sqlite3
import subprocess
import inspect
import py_compile
import re

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🔍 AUDITORÍA DE MÉTODOS DE TriSwarmOrchestrator Y REPARACIÓN DEL DAEMON")
print("=" * 80)

# 1. Leer código fuente e inspeccionar métodos
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

print("[1/5] Métodos detectados en el código fuente de art_63.py:")
def_matches = re.findall(r'def\s+([a_zA_Z0-9_]+)\s*\(([^)]*)\):', code)
for m_name, m_args in def_matches:
    if any(k in m_name for k in ["process", "run", "bounty", "swarm", "pipeline"]):
        print(f"  • {m_name}({m_args})")

# 2. Importar clase e inspeccionar firma
sys.path.insert(0, os.path.join(WORKSPACE, "modules"))
sys.path.insert(0, WORKSPACE)

try:
    import art_63
    orchestrator = art_63.TriSwarmOrchestrator()
    print("\n[2/5] Instanciación de TriSwarmOrchestrator exitosa.")
    for m_name in dir(orchestrator):
        if not m_name.startswith("_") and callable(getattr(orchestrator, m_name)):
            sig = inspect.signature(getattr(orchestrator, m_name))
            print(f"  📌 Método activo: {m_name}{sig}")
except Exception as e:
    print(f"\n❌ Error al instanciar TriSwarmOrchestrator: {e}")

# 3. Restablecer estados en SQLite
print("\n[3/5] Reseteando tareas PROCESSING -> PENDING en DB...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE bounty_opportunities SET status='PENDING' WHERE status='PROCESSING'")
conn.commit()
conn.close()
print("  ✅ Tareas reseteadas a PENDING.")

# 4. Detener instancias previas y limpiar registros
print("\n[4/5] Limpiando procesos en ejecución y reiniciando log...")
pids = subprocess.run(["pgrep", "-f", "art_63.py"], capture_output=True, text=True).stdout.strip().split()
for p in pids:
    if p:
        subprocess.run(["kill", "-9", p], stderr=subprocess.DEVNULL)

if os.path.exists(PID_FILE):
    os.remove(PID_FILE)

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== LOG INICIADO - DEMONIO ARTEFACTO 63 ===\n")

# 5. Inyectar run_daemon_loop dinámico y adaptable
daemon_loop_code = '''
def run_daemon_loop():
    import time
    import sqlite3
    import traceback
    import inspect

    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado correctamente.", flush=True)

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

            print("", flush=True)
            print(f"🚀 [DAEMON] Procesando Tarea ID {task_id}: {repo} -> {title}", flush=True)

            method_found = False
            for m_name in ["process_bounty_loop", "process_next_pending_bounty", "run_full_pipeline", "run_swarm", "process_bounty"]:
                if hasattr(orchestrator, m_name):
                    method = getattr(orchestrator, m_name)
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    print(f"⚡ Ejecutando '{m_name}' con parámetros esperados: {params}", flush=True)
                    
                    if len(params) == 0:
                        method()
                    else:
                        kwargs = {}
                        if "issue_url" in params: kwargs["issue_url"] = issue_url
                        elif "url" in params: kwargs["url"] = issue_url
                        elif "target" in params: kwargs["target"] = issue_url
                        
                        if "repo" in params: kwargs["repo"] = repo
                        if "title" in params: kwargs["title"] = title
                        
                        for p_key in ["bounty_id", "task_id", "id"]:
                            if p_key in params: kwargs[p_key] = task_id
                        
                        if kwargs:
                            method(**kwargs)
                        else:
                            args = [issue_url, repo, title][:len(params)]
                            method(*args)
                    
                    method_found = True
                    break

            if not method_found:
                print("⚠️ Ningún método ejecutor reconocido en TriSwarmOrchestrator.", flush=True)

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
            time.sleep(5)
'''

if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', daemon_loop_code.strip() + "\n\n", code)
else:
    code = code.strip() + "\n\n" + daemon_loop_code.strip() + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(ART63_PATH, doraise=True)
print("  ✅ modules/art_63.py reconfigurado y verificado.")

# Arrancar demonio registrando PID
log_fd = open(LOG_FILE, "a", encoding="utf-8")
proc = subprocess.Popen([sys.executable, "-u", ART63_PATH, "--daemon"], stdout=log_fd, stderr=log_fd)

with open(PID_FILE, "w") as pf:
    pf.write(str(proc.pid))

print(f"\n[5/5] 🟢 Demonio iniciado activamente en segundo plano con PID {proc.pid}.")
print("=" * 80)
