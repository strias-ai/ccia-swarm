import sqlite3
import uuid
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="CCIA Synthetic Data Metered API")
DB_PATH = "/home/k1/ccia_workspace/university.db"

@app.post("/v1/datasets/generate")
async def generate_dataset(records: int = 100, x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key requerida")
    
    # Generación sintética y reporte de consumo
    batch_id = str(uuid.uuid4())
    cost_per_record = 0.001
    total_billed = round(records * cost_per_record, 4)
    
    return {
        "batch_id": batch_id,
        "records_generated": records,
        "stripe_metered_cost_usd": total_billed,
        "status": "DELIVERED"
    }
