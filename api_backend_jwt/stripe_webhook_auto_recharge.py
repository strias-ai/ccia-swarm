# -*- coding: utf-8 -*-
"""
"""
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def process_stripe_event(event_payload):
    event_type = event_payload.get("type", "checkout.session.completed")
    data = event_payload.get("data", {}).get("object", {})
    client_key = data.get("client_reference_id") or data.get("customer_email")
    amount_paid = data.get("amount_total", 1500) / 100 # Default $15
    credits_to_add = int(amount_paid * 100) # 100 créditos por $1

    if not client_key:
        return {"status": "FAILED", "reason": "Falta referencia de cliente en payload."}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE api_clients 
        SET credits = credits + ? 
        WHERE api_key = ? OR client_name LIKE ?
    """, (credits_to_add, client_key, f"%{client_key}%"))
    
    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated > 0:
        return {"status": "SUCCESS", "added_credits": credits_to_add, "client": client_key}
    return {"status": "NOT_FOUND", "client": client_key}

if __name__ == "__main__":
    test_event = {
        "type": "checkout.session.completed",
        "data": {"object": {"customer_email": "FinTech Startup X", "amount_total": 2500}}
    }
    print("⚡ [STRIPE WEBHOOK v1.0.0] Procesando evento de pago simularlo:")
    print(json.dumps(process_stripe_event(test_event), indent=2))
