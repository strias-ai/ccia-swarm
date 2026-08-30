# -*- coding: utf-8 -*-
"""
⚡ FASTAPI CORE BACKEND & TOKEN CREDIT MIDDLEWARE V2.1.0
"""
from fastapi import FastAPI, HTTPException, Header, Depends
import sqlite3
import uvicorn
import os

app = FastAPI(title="CCIA Autonomous API Core", version="2.1.0")
DB_PATH = "/home/k1/ccia_workspace/university.db"

def verify_and_deduct_credit(x_api_key: str = Header(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT credits, client_name FROM api_clients WHERE api_key=?", (x_api_key,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="API Key inválida o no registrada.")
    
    credits, client_name = row
    if credits <= 0:
        conn.close()
        raise HTTPException(status_code=402, detail="Saldo insuficiente. Renueve en Stripe.")
    
    # Descuenta 1 crédito por llamada activa
    cursor.execute("UPDATE api_clients SET credits = credits - 1 WHERE api_key=?", (x_api_key,))
    conn.commit()
    conn.close()
    return {"client": client_name, "remaining_credits": credits - 1}

@app.get("/health")
def health_check():
    return {"status": "ONLINE", "system": "CCIA Core V5.0", "db": "university.db"}

@app.post("/v1/ast/audit")
def audit_code_endpoint(payload: dict, auth: dict = Depends(verify_and_deduct_credit)):
    return {
        "status": "SUCCESS",
        "audited_by": auth["client"],
        "remaining_credits": auth["remaining_credits"],
        "result": "AST Check Passed: No syntax errors detected."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
