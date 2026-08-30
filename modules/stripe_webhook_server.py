# -*- coding: utf-8 -*-
"""
CCiA Stripe Webhook Server
Recibe notificaciones en tiempo real cuando un cliente completa un pago.
"""

import os
import sys
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "/home/k1/ccia_workspace/university.db"

def load_env():
    env_file = "/home/k1/ccia_workspace/.env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

class StripeWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        load_env()
        secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)
        sig_header = self.headers.get('Stripe-Signature', '')
        
        try:
            import stripe
            stripe.api_key = secret_key
            if webhook_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            else:
                event = json.loads(payload.decode('utf-8'))
                
            event_type = event.get('type')
            print(f"📥 Evento Recibido de Stripe: {event_type}")
            
            if event_type in ['checkout.session.completed', 'payment_intent.succeeded']:
                data = event['data']['object']
                customer_email = data.get('customer_details', {}).get('email') or data.get('receipt_email')
                amount = data.get('amount_total', 0) / 100.0 or data.get('amount', 0) / 100.0
                currency = data.get('currency', 'eur').upper()
                
                # Registrar en la base de datos de telemetría y activar cliente
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO vant_agent_telemetry (agent_name, action, status, payload_raw)
                    VALUES ('StripeWebhook', 'PAYMENT_RECEIVED', 'SUCCESS', ?)
                """, (json.dumps({"email": customer_email, "amount": amount, "currency": currency}),))
                
                cur.execute("""
                    UPDATE microsaas_tenants SET status='ACTIVE' WHERE company_name LIKE ? OR domain LIKE ?
                """, (f"%{customer_email}%", f"%{customer_email}%"))
                
                conn.commit()
                conn.close()
                print(f"🟢 ¡PAGO CONFIRMADO! {amount} {currency} de {customer_email}. Inquilino activado.")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except Exception as e:
            print(f"⚠️ Error procesando Webhook: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

def run_server(port=4242):
    server_address = ('', port)
    httpd = HTTPServer(server_address, StripeWebhookHandler)
    print(f"🚀 Servidor de Webhooks escuchando en puerto {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
