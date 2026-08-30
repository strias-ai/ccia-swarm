import sqlite3
import stripe
import sys
import os

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_idempotency_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_stripe_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def process_webhook_event(payload, sig_header, endpoint_secret):
    init_idempotency_db()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return {"status": "error", "reason": f"Firma inválida: {str(e)}"}, 400

    event_id = event['id']
    event_type = event['type']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Comprobar idempotencia
    cursor.execute("SELECT event_id FROM processed_stripe_events WHERE event_id = ?", (event_id,))
    if cursor.fetchone():
        conn.close()
        return {"status": "ignored", "reason": "Evento ya procesado previamente"}, 200

    if event_type == 'payment_intent.succeeded':
        intent = event['data']['object']
        amount = intent['amount']
        
        # Registrar evento procesado
        cursor.execute(
            "INSERT INTO processed_stripe_events (event_id, event_type, amount) VALUES (?, ?, ?)",
            (event_id, event_type, amount)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "processed_amount": amount}, 200
        
    conn.close()
    return {"status": "unhandled_event"}, 200

if __name__ == "__main__":
    init_idempotency_db()
    print("✅ Tabla de Idempotencia verificada e inicializada en university.db")
