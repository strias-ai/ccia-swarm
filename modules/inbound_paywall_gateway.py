#!/usr/bin/env python3
"""
CCiA Artifact 35: Inbound Paywall & Public Webhook Revenue Gateway v1.0.0
Genera enlaces de pago públicos (Stripe Payment Links) para los servicios del CCIA.
"""

import os
import sqlite3
import stripe

DB_PATH = "/home/k1/ccia_workspace/university.db"

def get_stripe_key():
    # 1. Intentar desde variables de entorno
    key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
    if key and (key.startswith("sk_live_") or key.startswith("sk_test_")):
        return key

    # 2. Buscar en system_credentials
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(system_credentials);")
            cols = [c[1] for c in cur.fetchall()]
            
            if "secret_key" in cols:
                cur.execute("SELECT secret_key FROM system_credentials WHERE secret_key LIKE 'sk_live_%' OR secret_key LIKE 'sk_test_%' ORDER BY CASE WHEN secret_key LIKE 'sk_live_%' THEN 1 ELSE 2 END LIMIT 1")
            elif "credential_value" in cols:
                cur.execute("SELECT credential_value FROM system_credentials WHERE credential_value LIKE 'sk_live_%' OR credential_value LIKE 'sk_test_%' ORDER BY CASE WHEN credential_value LIKE 'sk_live_%' THEN 1 ELSE 2 END LIMIT 1")
            else:
                cur.execute("SELECT * FROM system_credentials LIMIT 1;")
            
            row = cur.fetchone()
            conn.close()
            if row:
                for item in row:
                    if isinstance(item, str) and (item.startswith("sk_live_") or item.startswith("sk_test_")):
                        return item
        except Exception:
            pass

    # 3. Leer desde .env
    env_paths = ["/home/k1/ccia_workspace/.env", "/home/k1/ccia_workspace/api_backend_jwt/.env"]
    for path in env_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if line.startswith("STRIPE_SECRET_KEY=") or line.startswith("STRIPE_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.startswith("sk_"):
                            return val
    return None

def create_public_service_product():
    api_key = get_stripe_key()
    if not api_key:
        print("❌ No se encontró API Key válida de Stripe en system_credentials ni en .env.")
        return

    stripe.api_key = api_key
    mode_str = "🟢 LIVE" if api_key.startswith("sk_live_") else "🟡 TEST"
    print(f"🔑 Usando Stripe Key [{mode_str}]: {api_key[:14]}...")

    try:
        # Catálogo de Servicios CCIA
        services = [
            {"name": "CCiA Code Audit Unit", "desc": "Auditoría autónoma de código y parche de seguridad", "price_usd": 15.00},
            {"name": "CCiA Agent Execution Pass", "desc": "Ejecución de tarea personalizada por enjambre A2A", "price_usd": 5.00}
        ]

        print("\n==========================================================================")
        print("🚀 CATALOGO DE PRODUCTOS Y PAYMENT LINKS CCIA")
        print("==========================================================================")

        for srv in services:
            product = stripe.Product.create(
                name=srv["name"],
                description=srv["desc"],
            )
            price = stripe.Price.create(
                unit_amount=int(srv["price_usd"] * 100),
                currency="usd",
                product=product.id,
            )
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}],
            )
            print(f"📦 Producto: {srv['name']} (${srv['price_usd']} USD)")
            print(f"🔗 Enlace de Pago Directo: {payment_link.url}\n")

        print("==========================================================================\n")

    except Exception as e:
        print(f"❌ Error en la API de Stripe: {e}")

if __name__ == "__main__":
    create_public_service_product()
