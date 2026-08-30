# -*- coding: utf-8 -*-
"""
CCIA STRIPE BILLING ENGINE v1.0
Gestión de Checkout, Suscripciones y Emisión de API Keys tras Pago Exitoso.
"""
import sqlite3
import uuid

DB_PATH = "/home/k1/ccia_workspace/university.db"

def process_mock_checkout(client_name: str, plan_amount: float) -> dict:
    # Generar API Key comercial
    new_api_key = f"ccia-live-{uuid.uuid4().hex[:12]}"
    credits = 10000 if plan_amount >= 499 else 1000
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO api_clients (api_key, client_name, credits) VALUES (?, ?, ?)",
        (new_api_key, client_name, credits)
    )
    conn.commit()
    conn.close()

    return {
        "status": "SUCCESS",
        "payment_status": "PAID_MOCK_STRIPE",
        "amount_received": f"{plan_amount} EUR",
        "client_name": client_name,
        "issued_api_key": new_api_key,
        "allocated_credits": credits,
        "invoice_url": f"https://ccia.ai/invoices/inv_{uuid.uuid4().hex[:8]}"
    }
