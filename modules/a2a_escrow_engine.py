import sqlite3
import uuid
from fastapi import FastAPI, Header, HTTPException, BaseModel

app = FastAPI(title="CCIA A2A Micro-Transactions & Outcome Escrow Engine")
DB_PATH = "/home/k1/ccia_workspace/university.db"

class EscrowJob(BaseModel):
    agent_id: str
    target_task: str
    bounty_usd: float

@app.post("/v1/a2a/escrow/create")
async def create_escrow(job: EscrowJob, x_agent_signature: str = Header(None)):
    if not x_agent_signature:
        raise HTTPException(status_code=401, detail="Firma A2A requerida")
    
    escrow_id = f"escrow_{uuid.uuid4().hex[:8]}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bounties (repo_name, bounty_amount, status, created_at)
        VALUES (?, ?, 'HELD_IN_ESCROW', datetime('now'))
    """, (f"a2a:{job.target_task}:{escrow_id}", job.bounty_usd))
    conn.commit()
    conn.close()
    
    return {
        "escrow_id": escrow_id,
        "status": "HELD_IN_ESCROW",
        "amount_usd": job.bounty_usd,
        "message": "Fondos en custodia. Se liberarán al verificar el Proof of Outcome."
    }

@app.post("/v1/a2a/escrow/release/{escrow_id}")
async def release_escrow(escrow_id: str, test_passed: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if test_passed:
        cursor.execute("UPDATE bounties SET status='CLAIMED' WHERE repo_name LIKE ?", (f"%{escrow_id}%",))
        conn.commit()
        conn.close()
        return {"escrow_id": escrow_id, "status": "RELEASED_TO_AGENT", "payout": "SUCCESS"}
    else:
        cursor.execute("UPDATE bounties SET status='REFUNDED' WHERE repo_name LIKE ?", (f"%{escrow_id}%",))
        conn.commit()
        conn.close()
        return {"escrow_id": escrow_id, "status": "REFUNDED", "payout": "CANCELLED"}
