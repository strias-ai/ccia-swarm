# -*- coding: utf-8 -*-
"""
CCIA MONETIZATION & RATE LIMIT GUARD v1.0
Gestión de clientes, validador de X-API-Key y control de créditos.
"""
import sqlite3
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_monetization_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_clients (
            api_key TEXT PRIMARY KEY,
            client_name TEXT NOT NULL,
            credits INTEGER DEFAULT 100,
            total_requests INTEGER DEFAULT 0
        )
    ''')
    # Clave de desarrollo previa para pruebas
    cursor.execute("INSERT OR IGNORE INTO api_clients (api_key, client_name, credits) VALUES ('ccia-dev-key-999', 'Demo Client', 50)")
    conn.commit()
    conn.close()

async def verify_api_key_middleware(request: Request, call_next):
    # Rutas públicas sin cobro
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Encabezado X-API-Key ausente."})

    init_monetization_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT credits, total_requests FROM api_clients WHERE api_key=?", (api_key,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse(status_code=403, content={"detail": "API Key inválida o revocada."})

    credits, total_reqs = row
    if credits <= 0:
        conn.close()
        return JSONResponse(status_code=429, content={"detail": "Cuota agotada. Recargue créditos para continuar."})

    # Descontar 1 crédito por petición
    cursor.execute("UPDATE api_clients SET credits = credits - 1, total_requests = total_requests + 1 WHERE api_key=?", (api_key,))
    conn.commit()
    conn.close()

    response = await call_next(request)
    return response
