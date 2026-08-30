import sqlite3
import stripe
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_db():
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            user_email TEXT PRIMARY KEY,
            stripe_customer_id TEXT,
            status TEXT NOT NULL DEFAULT 'free',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/v1/stripe/webhook':
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length).decode('utf-8')
            sig_header = self.headers.get('Stripe-Signature', '')
            endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

            try:
                if endpoint_secret and sig_header:
                    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
                else:
                    event = json.loads(payload)
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                return

            event_id = event.get('id')
            event_type = event.get('type')

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT event_id FROM processed_stripe_events WHERE event_id = ?", (event_id,))
            
            if cursor.fetchone():
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "ignored", "reason": "duplicate_event"}')
                return

            if event_type == 'payment_intent.succeeded':
                intent = event['data']['object']
                amount = intent.get('amount', 0)
                metadata = intent.get('metadata', {})
                user_email = metadata.get('user_email', 'guest@ccia.edu')
                customer_id = intent.get('customer', '')

                cursor.execute(
                    "INSERT INTO processed_stripe_events (event_id, event_type, amount) VALUES (?, ?, ?)",
                    (event_id, event_type, amount)
                )
                cursor.execute(
                    "INSERT INTO user_subscriptions (user_email, stripe_customer_id, status) VALUES (?, ?, 'active') "
                    "ON CONFLICT(user_email) DO UPDATE SET status='active', updated_at=CURRENT_TIMESTAMP",
                    (user_email, customer_id)
                )
                conn.commit()

            elif event_type == 'customer.subscription.deleted':
                obj = event['data']['object']
                metadata = obj.get('metadata', {})
                user_email = metadata.get('user_email', '')
                if user_email:
                    cursor.execute(
                        "INSERT INTO processed_stripe_events (event_id, event_type, amount) VALUES (?, ?, 0)",
                        (event_id, event_type)
                    )
                    cursor.execute(
                        "UPDATE user_subscriptions SET status='cancelled', updated_at=CURRENT_TIMESTAMP WHERE user_email = ?",
                        (user_email,)
                    )
                    conn.commit()

            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        else:
            self.send_response(404)
            self.end_headers()

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    init_db()
    server = ReusableHTTPServer(('0.0.0.0', 8080), WebhookHandler)
    server.serve_forever()
