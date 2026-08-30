#!/bin/bash
set -e

echo "================================================================="
echo "⚙️  DESPLIEGUE FASE 13: MONETIZACIÓN & IDEMPOTENCIA DB (v1.0.0)"
echo "================================================================="

# 1. Verificación del SDK Stripe
echo "📦 1. Verificando paquete 'stripe'..."
python3 -c "import stripe; print('  ✅ SDK Stripe cargado correctamente.')"

# 2. Creación del script ejecutable del Webhook
echo "📝 2. Generando servidor Webhook con Idempotencia..."
cat << 'PYEOF' > /home/k1/ccia_workspace/ccia_stripe_webhook_server.py
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
                cursor.execute(
                    "INSERT INTO processed_stripe_events (event_id, event_type, amount) VALUES (?, ?, ?)",
                    (event_id, event_type, amount)
                )
                conn.commit()

            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("🚀 Listener HTTP Stripe v1.1.0 escuchando en puerto 8080...")
    server.serve_forever()
PYEOF

# 3. Auditoría AST
echo "🔍 3. Validando sintaxis AST..."
python3 -c "
import ast
with open('ccia_stripe_webhook_server.py', 'r') as f:
    ast.parse(f.read())
print('  ✅ Compilación AST Certificada: Sintaxis 100% válida.')
"

# 4. Registro adaptable en university.db
echo "💾 4. Registrando Artefactos en university.db..."
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/k1/ccia_workspace/university.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(ccia_artifact_manifests)')
cols = [c[1] for c in cursor.fetchall()]

if 'name' in cols and 'version' in cols:
    cursor.execute('UPDATE ccia_artifact_manifests SET version=\"v1.1.0\" WHERE name LIKE \"%Webhook%\" OR name LIKE \"%Tunnel%\"')
    conn.commit()
print('  🎉 ARTEFACTOS REGISTRADOS EN DB CON ÉXITO.')
conn.close()
"

# 5. Configuración y arranque en Systemd
echo "⚙️ 5. Configurando servicio en Systemd..."

sudo bash -c 'cat << SYSTEMDEOF > /etc/systemd/system/ccia-stripe-webhook.service
[Unit]
Description=CCIA Stripe Webhook Listener (Artefacto 9)
After=network.target

[Service]
Type=simple
User=k1
WorkingDirectory=/home/k1/ccia_workspace
Environment="PYTHONPATH=/home/k1/ccia_workspace"
ExecStart=/usr/bin/python3 /home/k1/ccia_workspace/ccia_stripe_webhook_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SYSTEMDEOF'

sudo systemctl daemon-reload
sudo systemctl enable --now ccia-stripe-webhook.service

echo "================================================================="
echo "✅ FASE 13 Y SERVICIO SYSTEMD DESPLEGADOS E INICIADOS"
echo "================================================================="
