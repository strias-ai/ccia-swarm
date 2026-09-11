import os
import re
import py_compile

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

daemon_loop_clean = """
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
            
            print("", flush=True)
            print(f"🚀 [DAEMON] Procesando Tarea ID {task_id}: {repo} -> {title}", flush=True)
            
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
            print(f"✅ [DAEMON] Tarea ID {task_id} marcada como COMPLETED.", flush=True)
            print("", flush=True)
            
        except Exception as e:
            print(f"❌ Error en bucle daemon: {e}", flush=True)
            time.sleep(5)
"""

if "def run_daemon_loop" in code:
    code = re.sub(r'def run_daemon_loop\(\):[\s\S]*?(?=\nif __name__ ==|\Z)', daemon_loop_clean.strip() + "\n\n", code)
else:
    code += "\n\n" + daemon_loop_clean.strip() + "\n"

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("=" * 80)
print("🛠️ SINTAXIS DE F-STRING CORREGIDA EN ARTEFACTO 63")
print("=" * 80)

try:
    py_compile.compile(art63_path, doraise=True)
    print("  ✅ modules/art_63.py COMPILA CORRECTAMENTE.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación residual:\n{e}")

try:
    py_compile.compile(mando_path, doraise=True)
    print("  ✅ ccia_mando_63.py COMPILA CORRECTAMENTE.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación en mando:\n{e}")

print("=" * 80)
