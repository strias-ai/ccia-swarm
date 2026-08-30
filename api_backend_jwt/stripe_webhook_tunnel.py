# -*- coding: utf-8 -*-
"""
"""
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def handle_stripe_webhook(payload):
    # Simula la recepción de evento checkout.session.completed de Stripe
    client_email = payload.get("customer_email", "cliente@demo.com")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE api_clients SET credits = credits + 1000 WHERE client_name LIKE ?", (f"%{client_email}%",))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "message": f"1000 créditos recargados para {client_email}"}

if __name__ == "__main__":
    print("📡 [WEBHOOK LISTENER v1.0.0] Probando recarga de saldo simularia...")
    res = handle_stripe_webhook({"customer_email": "Demo"})
    print("✅ Resultado Webhook:", json.dumps(res, indent=2))
