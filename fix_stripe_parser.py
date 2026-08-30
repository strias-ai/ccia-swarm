# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import py_compile

ENV_PATH = "/home/k1/ccia_workspace/.env"
MODULES_DIR = "/home/k1/ccia_workspace/modules"

def load_env():
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

env = load_env()
sk = env.get("STRIPE_SECRET_KEY", "")
public_url = env.get("PUBLIC_DOMAIN_URL", "").rstrip("/")

print("⚡ Probando API de Stripe con decodificación de objeto en vivo...")

try:
    import stripe
    stripe.api_key = sk
    balance_obj = stripe.Balance.retrieve()
    balance = balance_obj.to_dict() if hasattr(balance_obj, "to_dict") else dict(balance_obj)
    
    print("\n✅ Conexión Exitosa con Stripe API (LIVE)")
    print("📊 Saldo Real Disponible en Cuenta Banco/Stripe:")
    
    avail = balance.get("available", [])
    pend = balance.get("pending", [])
    
    if not avail and not pend:
        print("   • Sin fondos pendientes ni disponibles acumulados.")
    else:
        for item in avail:
            print(f"   • Disponible: {item['amount']/100.0:.2f} {item['currency'].upper()}")
        for item in pend:
            print(f"   • Pendiente de Transferencia: {item['amount']/100.0:.2f} {item['currency'].upper()}")

except Exception as e:
    print(f"🔴 Error procesando respuesta Stripe: {e}")

# Actualizar módulo microsaas_deployer.py
microsaas_path = os.path.join(MODULES_DIR, "microsaas_deployer.py")
if os.path.exists(microsaas_path):
    with open(microsaas_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    old_code = "balance = stripe.Balance.retrieve()"
    new_code = "balance_obj = stripe.Balance.retrieve()\n        balance = balance_obj.to_dict() if hasattr(balance_obj, 'to_dict') else dict(balance_obj)"
    
    if old_code in content and "balance_obj" not in content:
        content = content.replace(old_code, new_code)
        with open(microsaas_path, "w", encoding="utf-8") as f:
            f.write(content)
        py_compile.compile(microsaas_path, doraise=True)
        print("🟢 `microsaas_deployer.py` parcheado y verificado en AST.")

clean_webhook_url = public_url if public_url.endswith("/webhook") else f"{public_url}/webhook"

print("\n" + "="*78)
print("📌 URL EXACTA PARA REGISTRAR EN STRIPE DASHBOARD:")
print(f"   👉 {clean_webhook_url}")
print("="*78)
