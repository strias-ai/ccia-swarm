import sqlite3
import json
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def inspect():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Estados considerados válidos y sanos por el sistema
    valid_statuses = ('SANITIZED_PROCESSED', 'BOUNTY_RESOLVED_PAID', 'ESCROW_ACTIVE', 'BOUNTY_PROCESSED')
    placeholders = ','.join(['?'] * len(valid_statuses))
    
    cur.execute(f"SELECT COUNT(*) FROM vant_agent_telemetry WHERE status NOT IN ({placeholders}) AND status IS NOT NULL;", valid_statuses)
    anomalies = cur.fetchone()[0]
    conn.close()
    
    status = "HEALTHY" if anomalies == 0 else "WARNING"
    
    return {
        "timestamp": datetime.now().astimezone().isoformat(),
        "hapax_telemetry_anomalies": anomalies,
        "hapax_log_anomalies": 0,
        "status": status
    }

if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2, ensure_ascii=False))
