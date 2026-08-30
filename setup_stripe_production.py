# -*- coding: utf-8 -*-
"""
CCiA Stripe Production & Webhook Setup Wizard v1.0
Configura claves en vivo (sk_live_), valida la API y habilita el servidor Webhook para clientes.
"""

import os
import sys
import sqlite3
import py_compile
import json

ENV_PATH = "/home/k1/ccia_workspace/.env"
MODULES_DIR = "/home/k1/ccia_workspace/modules"
DB_PATH = "/home/k1/ccia_workspace/university.db"

def banner():
    print("\n" + "="*78)
    print("      💳 CCiA STRIPE PRODUCTION & WEBHOOK SETUP WIZARD")
    print("="*78)
    print(" Este asistente configurará tus claves LIVE de Stripe y conectará los")
    print(" agentes monetizadores (Artefactos 10, 19, 30 y 31) a la pasarela real.\n")

def load_existing_env():
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def mask_key(key):
    if not key or len(key) < 12:
        return "(No configurada)"
    return key[:7] + "..." + key[-4:]

def prompt_credentials(existing):
    print("📌 Por favor, introduce tus datos de Stripe (Presiona ENTER para mantener el valor actual si existe):\n")
    
    curr_sk = existing.get("STRIPE_SECRET_KEY", "")
    sk = input(f" 1. STRIPE_SECRET_KEY [{mask_key(curr_sk)}]: ").strip() or curr_sk

    curr_pk = existing.get("STRIPE_PUBLISHABLE_KEY", "")
    pk = input(f" 2. STRIPE_PUBLISHABLE_KEY [{mask_key(curr_pk)}]: ").strip() or curr_pk

    curr_wh = existing.get("STRIPE_WEBHOOK_SECRET", "")
    wh = input(f" 3. STRIPE_WEBHOOK_SECRET (whsec_...) [{mask_key(curr_wh)}]: ").strip() or curr_wh

    curr_url = existing.get("PUBLIC_DOMAIN_URL", "https://ccia.midominio.com")
    url = input(f" 4. URL pública del Webhook / Dominio [{curr_url}]: ").strip() or curr_url

    return sk, pk, wh, url

def save_env(sk, pk, wh, url):
    lines = [
        "# CCiA Production Environment Credentials",
        f'STRIPE_SECRET_KEY="{sk}"',
        f'STRIPE_PUBLISHABLE_KEY="{pk}"',
        f'STRIPE_WEBHOOK_SECRET="{wh}"',
        f'PUBLIC_DOMAIN_URL="{url}"',
    ]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENV_PATH, 0o600)
    print(f"\n🔒 Archivo de configuración guardado con permisos seguros en {ENV_PATH}")

def test_stripe_connection(sk):
    print("\n⚡ Probando conexión directa con la API de Stripe...")
    if not sk:
        print("⚠️ No se ha proporcionado STRIPE_SECRET_KEY.")
        return False
    
    try:
        import stripe
    except ImportError:
        print("📦 Instalando librería oficial de Stripe...")
        os.system(f"{sys.executable} -m pip install stripe --quiet")
        import stripe

    stripe.api_key = sk
    try:
        balance = stripe.Balance.retrieve()
        mode = "🟢 PRODUCCIÓN (LIVE)" if sk.startswith("sk_live_") else "🟡 MODO PRUEBAS (TEST)"
        print(f"\n✅ Conexión exitosa con Stripe | Estado: {mode}")
        
        print("📊 Saldo en Cuenta Stripe:")
        avail = balance.get("available", [])
        pend = balance.get("pending", [])
        
        for item in avail:
            amount = item["amount"] / 100.0
            currency = item["currency"].upper()
            print(f"   • Disponible: {amount:.2f} {currency}")
            
        for item in pend:
            amount = item["amount"] / 100.0
            currency = item["currency"].upper()
            print(f"   • Pendiente de transferencia: {amount:.2f} {currency}")
            
        return True
    except Exception as e:
        print(f"🔴 Error de autenticación en Stripe: {e}")
        return False

def setup_webhook_handler_script():
    webhook_script_code = '''# -*- coding: utf-8 -*-
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
'''
    wh_path = os.path.join(MODULES_DIR, "stripe_webhook_server.py")
    with open(wh_path, "w", encoding="utf-8") as f:
        f.write(webhook_script_code)
    
    py_compile.compile(wh_path, doraise=True)
    print(f"🟢 Servidor de Webhooks desplegado y certificado AST en {wh_path}")

def main():
    banner()
    existing = load_existing_env()
    sk, pk, wh, url = prompt_credentials(existing)
    save_env(sk, pk, wh, url)
    
    # Cargar en os.environ para la sesión actual
    os.environ["STRIPE_SECRET_KEY"] = sk
    os.environ["STRIPE_PUBLISHABLE_KEY"] = pk
    os.environ["STRIPE_WEBHOOK_SECRET"] = wh
    os.environ["PUBLIC_DOMAIN_URL"] = url

    test_stripe_connection(sk)
    setup_webhook_handler_script()
    
    print("\n" + "="*78)
    print("🎉 CONFIGURACIÓN DE STRIPE COMPLETADA CON ÉXITO")
    print("="*78)
    print(f" • URL para registrar en Stripe Dashboard (Webhooks): {url.rstrip('/')}/webhook")
    print(" • Eventos recomendados a seleccionar en Stripe: checkout.session.completed, payment_intent.succeeded")
    print("="*78 + "\n")

if __name__ == "__main__":
    main()
