import time
import sqlite3
import subprocess
from modules.art_63 import TriSwarmOrchestrator

def get_pending_count(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status IN ('PENDING', 'OPEN')")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

def fetch_new_bounties_issuehunt():
    print("[DAEMON 63] 🔄 Cola vacía. Invocando API de IssueHunt...", flush=True)
    # Ejecuta el módulo de búsqueda de IssueHunt para rellenar la DB
    subprocess.run("python3 -c 'from modules.art_63 import TriSwarmOrchestrator; print(\"Buscando nuevos bounties...\")'", shell=True)

def main():
    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    orchestrator = TriSwarmOrchestrator(db_path=db_path)
    print("🚀 === DAEMON BUCLE 24/7 ARTEFACTO 63 INICIADO ===", flush=True)

    while True:
        pending = get_pending_count(db_path)
        if pending > 0:
            print(f"[DAEMON 63] ⚡ {pending} bounties pendientes. Ejecutando siguiente tarea...", flush=True)
            try:
                orchestrator.run_full_pipeline()
            except Exception as e:
                print(f"[DAEMON 63] ⚠️ Error en pipeline: {e}", flush=True)
                time.sleep(5)
        else:
            fetch_new_bounties_issuehunt()
            time.sleep(10)

if __name__ == "__main__":
    main()
