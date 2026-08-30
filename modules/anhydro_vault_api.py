from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import zlib
import base64
import json
import sqlite3
from datetime import datetime

router = APIRouter()
DB_PATH = "/home/k1/ccia_workspace/university.db"

class FreezeRequest(BaseModel):
    agent_id: str
    session_id: str
    context_data: dict

class HydrateRequest(BaseModel):
    agent_id: str
    session_id: str

@router.post("/freeze")
def freeze_agent_state(req: FreezeRequest):
    try:
        raw_json = json.dumps(req.context_data).encode("utf-8")
        compressed = zlib.compress(raw_json)
        encoded = base64.b64encode(compressed).decode("utf-8")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anhydro_vault (
                agent_id TEXT,
                session_id TEXT PRIMARY KEY,
                cold_data TEXT,
                original_bytes INT,
                compressed_bytes INT,
                frozen_at TIMESTAMP
            )
        """)
        cur.execute("""
            INSERT OR REPLACE INTO anhydro_vault 
            (agent_id, session_id, cold_data, original_bytes, compressed_bytes, frozen_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (req.agent_id, req.session_id, encoded, len(raw_json), len(compressed)))
        conn.commit()
        conn.close()
        
        savings = round((1 - (len(compressed) / len(raw_json))) * 100, 2) if len(raw_json) > 0 else 0
        return {
            "status": "FROZEN",
            "session_id": req.session_id,
            "original_bytes": len(raw_json),
            "compressed_bytes": len(compressed),
            "ram_savings_percent": f"{savings}%",
            "metered_cost_usd": 0.001
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hydrate")
def hydrate_agent_state(req: HydrateRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT cold_data FROM anhydro_vault WHERE agent_id=? AND session_id=?", (req.agent_id, req.session_id))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Estado anhidro no encontrado.")
            
        compressed = base64.b64decode(row[0].encode("utf-8"))
        decompressed = zlib.decompress(compressed)
        context_data = json.loads(decompressed.decode("utf-8"))
        
        return {
            "status": "HYDRATED",
            "session_id": req.session_id,
            "context_data": context_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
