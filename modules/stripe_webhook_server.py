#!/usr/bin/env python3
from flask import Flask, request, jsonify
import sqlite3
import stripe
import time
import os

app = Flask(__name__)

DB_PATH = "/home/k1/ccia_workspace/university.db"
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

stripe.api_key = STRIPE_SECRET_KEY

def record_real_payment(event_id, event_type, amount_usd, tx_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS processed_stripe_events_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            event_type TEXT,
            amount_eur REAL,
            amount_usd REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        INSERT OR IGNORE INTO processed_stripe_events_v2 (event_id, event_type, amount_eur, amount_usd, status)
        VALUES (?, ?, ?, ?, 'COMPLETED')
    """, (event_id, event_type, amount_usd * 0.92, amount_usd))
    
    c.execute("""
        INSERT INTO revenue_settlements (source_event, amount_usd, agent_recipient, status, mode, signature_verified, tx_hash)
        VALUES (?, ?, 'CCIA_TREASURY_MAIN', 'SETTLED', 'REAL', 1, ?)
    """, (f"STRIPE_{event_type}", amount_usd, tx_id))
    
    conn.commit()
    conn.close()
    print(f"✅ [STRIPE LIVE] Pago Real Registrado: ${amount_usd:.2f} USD (ID: {event_id})")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "service": "CCiA Stripe Live Webhook Engine",
        "mode": "PRODUCTION_REAL",
        "port": 8088
    }), 200

@app.route('/v1/stripe/webhook', methods=['POST'])
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', None)

    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({"status": "error", "reason": "Webhook secret missing"}), 400

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 400

    event_type = event['type']
    event_id = event['id']
    
    if event_type in ['payment_intent.succeeded', 'checkout.session.completed']:
        data_obj = event['data']['object']
        amount_usd = data_obj.get('amount_received', data_obj.get('amount_total', 0)) / 100.0
        tx_id = data_obj.get('id', event_id)
        record_real_payment(event_id, event_type, amount_usd, tx_id)

    return jsonify({"status": "success", "event_id": event_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088)
