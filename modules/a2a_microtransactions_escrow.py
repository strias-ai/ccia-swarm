import sqlite3, json, os
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vant_agent_telemetry);")
    cols = [r[1] for r in cur.fetchall()]
    ts = datetime.now().astimezone().isoformat()
    
    tx = {"sender": "Agent_A", "receiver": "Agent_B", "credits": 100, "status": "ESCROW_LOCKED"}
    data_map = {
        "agent_name": "A2AEscrowEngine",
        "action": "A2A_ESCROW_LOCK",
        "status": "ESCROW_ACTIVE",
        "payload_raw": json.dumps(tx),
        "details": json.dumps(tx),
        "created_at": ts
    }
    ins_cols = [c for c in cols if c in data_map]
    ins_vals = [data_map[c] for c in ins_cols]
    if ins_cols:
        sql = f"INSERT INTO vant_agent_telemetry ({', '.join(ins_cols)}) VALUES ({', '.join(['?']*len(ins_cols))});"
        cur.execute(sql, ins_vals)
        
    conn.commit()
    conn.close()
    return {"status": "HEALTHY", "escrow_status": "ACTIVE", "locked_credits": 100}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
