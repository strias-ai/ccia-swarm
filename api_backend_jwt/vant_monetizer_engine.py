# -*- coding: utf-8 -*-
"""
Generación dinámica de ofertas comerciales por niveles y facturación automática.
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import os
import sys

DB_PATH = "/home/k1/ccia_workspace/university.db"

# Matriz de Monetización por Servicios VANT
PRICING_TIERS = {
    "basic": {
        "title": "Auditoría AST Estática Básica",
        "amount": "19900",  # 199.00 EUR
        "credits": 500
    },
    "pro": {
        "title": "Auditoría OWASP Completa + Auto-Fix AST",
        "amount": "49900",  # 499.00 EUR
        "credits": 2500
    },
    "enterprise": {
        "title": "Certificación Completa DevSecOps & Pipeline CI/CD",
        "amount": "99900",  # 999.00 EUR
        "credits": 10000
    }
}

def get_stripe_key():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT api_key FROM system_credentials WHERE service='STRIPE_SECRET_KEY' AND status='ACTIVE'")
        row = cursor.fetchone()
        conn.close()
        return row[0].strip() if row else None
    except Exception as e:
        print(f"❌ Error al consultar Stripe Secret Key: {e}")
        return None

def generate_monetization_offer(repo_name, tier="pro"):
    stripe_key = get_stripe_key()
    if not stripe_key:
        print("❌ No hay clave activa de Stripe en university.db.")
        return None

    tier_info = PRICING_TIERS.get(tier.lower(), PRICING_TIERS["pro"])
    product_name = f"{tier_info['title']} - [{repo_name}]"
    
    payload = {
        'payment_method_types[]': 'card',
        'line_items[0][price_data][currency]': 'eur',
        'line_items[0][price_data][product_data][name]': product_name,
        'line_items[0][price_data][unit_amount]': tier_info["amount"],
        'line_items[0][quantity]': '1',
        'mode': 'payment',
        'success_url': f'https://trycloudflare.com/success?repo={urllib.parse.quote(repo_name)}&tier={tier}&session_id={{CHECKOUT_SESSION_ID}}',
        'cancel_url': 'https://trycloudflare.com/cancel'
    }

    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request('https://api.stripe.com/v1/checkout/sessions', data=data, method='POST')
    req.add_header('Authorization', f'Bearer {stripe_key}')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            checkout_url = res_data.get('url')
            session_id = res_data.get('id')
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Registrar evento en Telemetría Comercial
            cursor.execute('''
                INSERT INTO vant_agent_telemetry (agent_name, action, status, payload)
                VALUES ('Cerrador_Monetizador_V2', 'OFFER_GENERATED', 'READY_FOR_PAYMENT', ?)
            ''', (f"Repo: {repo_name} | Tier: {tier.upper()} | Checkout: {checkout_url}",))
            
            # Asignar credenciales de acceso prepago al cliente
            api_key = f"ccia-live-{session_id[-10:]}"
            cursor.execute('''
                INSERT OR REPLACE INTO api_clients (client_name, api_key, credits, total_requests)
                VALUES (?, ?, ?, 0)
            ''', (repo_name, api_key, tier_info["credits"]))
            
            conn.commit()
            conn.close()
            
            return {
                "repo": repo_name,
                "tier": tier.upper(),
                "price": f"{int(tier_info['amount'])/100:.2f} EUR",
                "checkout_url": checkout_url,
                "api_key_provisioned": api_key,
                "credits_assigned": tier_info["credits"]
            }
    except Exception as e:
        print(f"❌ Error generando Checkout Session en Stripe: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Ejecutando Ciclo de Monetización Automática VANT V2...")
    sample_leads = [
        ("LemonQu-GIT/ChatGLM-6B-Engineering", "pro"),
        ("fastapi/fastapi-enterprise-template", "enterprise")
    ]
    
    for repo, tier in sample_leads:
        res = generate_monetization_offer(repo, tier)
        if res:
            print(f"\n💎 PROPUESTA CREADA EXITOSAMENTE:")
            print(f"  • Repo Target:        {res['repo']}")
            print(f"  • Nivel/Tier:         {res['tier']} ({res['price']})")
            print(f"  • Link Checkout:      {res['checkout_url']}")
            print(f"  • Créditos Asignados: {res['credits_assigned']} requests")
