# -*- coding: utf-8 -*-
"""
"""
import os
import sqlite3
import subprocess
import json
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"
ENV_PATH = "/home/k1/ccia_workspace/.env"

def setup_stripe_keys(pub_key=None, secret_key=None, webhook_sec=None):
    if not pub_key:
        pub_key = input("🔑 Ingresa tu Stripe Publishable Key (pk_live_... / pk_test_...): ").strip()
    if not secret_key:
        secret_key = input("🔐 Ingresa tu Stripe Secret Key (sk_live_... / sk_test_...): ").strip()
    if not webhook_sec:
        webhook_sec = input("⚓ Ingresa tu Stripe Webhook Secret (whsec_... [Opcional - Pulsar ENTER]): ").strip()

    env_content = f"""# CCIA STRIPE LIVE CONFIGURATION
STRIPE_PUBLISHABLE_KEY={pub_key}
STRIPE_SECRET_KEY={secret_key}
STRIPE_WEBHOOK_SECRET={webhook_sec}
"""
    with open(ENV_PATH, "w") as f:
        f.write(env_content)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS system_credentials (service TEXT PRIMARY KEY)")
    
    cursor.execute("PRAGMA table_info(system_credentials)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    needed_cols = {
        "api_key": "TEXT",
        "public_key": "TEXT",
        "secret_key": "TEXT",
        "webhook_secret": "TEXT",
        "updated_at": "TEXT"
    }
    
    for col, col_type in needed_cols.items():
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE system_credentials ADD COLUMN {col} {col_type}")

    now_str = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO system_credentials (service, api_key, public_key, secret_key, webhook_secret, updated_at)
        VALUES ('stripe', ?, ?, ?, ?, ?)
        ON CONFLICT(service) DO UPDATE SET
            api_key=excluded.api_key,
            public_key=excluded.public_key,
            secret_key=excluded.secret_key,
            webhook_secret=excluded.webhook_secret,
            updated_at=excluded.updated_at
    """, (secret_key, pub_key, secret_key, webhook_sec, now_str))
    
    conn.commit()
    conn.close()

    print("\n🔍 Validando claves con la API REST de Stripe...")
    cmd = f"curl -s -u {secret_key}: https://api.stripe.com/v1/balance"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        val_json = json.loads(res.stdout)
        if "object" in val_json and val_json["object"] == "balance":
            print("✅ ¡CONEXIÓN EXITOSA CON STRIPE! Cuenta autenticada correctamente.")
            return {"status": "SUCCESS", "account_balance": val_json.get("available", [])}
        elif "error" in val_json:
            print(f"⚠️ Alerta Stripe API: {val_json['error'].get('message')}")
            return {"status": "KEY_WARNING", "message": val_json['error'].get('message')}
    except Exception:
        pass

    print("💾 Credenciales guardadas correctamente en .env y university.db.")
    return {"status": "SAVED", "env_path": ENV_PATH}

if __name__ == "__main__":
    print("💳 [CCIA STRIPE LIVE CONFIGURATOR v1.0.0]")
    setup_stripe_keys()
