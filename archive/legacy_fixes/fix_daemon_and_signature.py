import os
import re
import sqlite3
import py_compile
import inspect

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
PID_FILE = "/tmp/art63_daemon.pid"
LOG_FILE = "/tmp/art63_reasoning.log"

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS Y FIRMA DE MÉTODOS EN ARTEFACTO 63")
print("=" * 80)

# 1. Resetear tareas bloqueadas en PROCESSING a PENDING
print("[1/4] Reseteando estado de tareas en DB...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE bounty_opportunities SET status='PENDING' WHERE status='PROCESSING'")
conn.commit()
conn.close()
print("  ✅ Tareas reseteadas a PENDING.")

# 2. Leer art_63.py para encontrar la firma exacta de métodos de TriSwarmOrchestrator
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

orchestrator_defs = re.findall(r'def\s+([a_zA_Z0-9_]+)\s*\(([^)]*)\)', code)
print("\n[2/4] Métodos detectados en el archivo:")
for name, params in orchestrator_defs:
    if any(k in name for k in ['process', 'run', 'bounty', 'pipeline', 'swarm']):
        print(f"  • {name}({params})")

# 3. Construir run_daemon_loop sin secuencias de escape conflictivas
daemon_loop_clean = '''
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

            print("", flush=True)
            print(f"🚀 [DAEMON] Procesando Tarea ID {task_id}: {repo} -> {title}", flush=True)

            # Invocar dinámicamente el método disponible adaptando la firma
            target_method = None
            for m_name in ["process_bounty_loop", "run_full_pipeline", "run_swarm", "process_bounty", "execute_bounty"]:
                if hasattr(orchestrator, m_name):
                    target_method = getattr(orchestrator, m_name)
                    break

            if target_method:
                sig = inspect.signature(target_method)
                param_names = list(sig.parameters.keys())

                kwargs = {}
                if "issue_url" in param_names:
                    kwargs["issue_url"] = issue_url
                elif "url" in param_names:
                    kwargs["url"] = issue_url
                elif "target" in param_names:
                    kwargs["target"] = issue_url

                if "repo" in param_names:
                    kwargs["repo"] = repo
                if "title" in param_names:
                    kwargs["title"] = title

                if kwargs:
                    target_method(**kwargs)
                else:
                    num_params = len(param_names)
                    if num_params == 0:
                        target_method()
                    elif num_params == 1:
                        target_method(issue_url)
                    elif num_params == 2:
                        target_method(issue_url, repo)
                    else:
                        target_method(issue_url, repo, title)
            else:
                print("⚠️ No se encontró método ejecutor compatible en TriSwarmOrchestrator.", flush=True)

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
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', daemon_loop_clean.strip() + "\n\n", code)
else:
    code = code.strip() + "\n\n" + daemon_loop_clean.strip() + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

# 4. Verificar compilación
print("\n[3/4] Verificando compilación...")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ modules/art_63.py compila correctamente sin errores de sintaxis.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
