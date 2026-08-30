# -*- coding: utf-8 -*-
import sqlite3
import urllib.request
import json
import os
import time

DB_PATH = '/home/k1/ccia_workspace/university.db'
LOG_PATH = '/home/k1/ccia_workspace/logs/stripe_webhooks.log'

def log_message(msg):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(formatted + '\n')

def get_stripe_key():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT secret_key, api_key FROM system_credentials 
        WHERE service IN ('stripe', 'STRIPE_SECRET_KEY') AND status = 'ACTIVE'
        ORDER BY CASE WHEN secret_key LIKE 'sk_live_%' THEN 1 ELSE 2 END LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    if row:
        key = row[0] if row[0] else row[1]
        if key and (key.startswith('sk_live_') or key.startswith('sk_test_')):
            return key
    return None

def fetch_stripe_data(endpoint, api_key):
    url = f"https://api.stripe.com/v1/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {api_key}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        log_message(f"⚠️ Error conectando con API de Stripe ({endpoint}): {str(e)}")
        return None

def run_stripe_sync():
    log_message("💳 [CCiA Live Stripe Sync] Consultando API oficial de Stripe...")
    
    api_key = get_stripe_key()
    if not api_key:
        log_message("❌ No se encontró una clave de API válida en system_credentials.")
        return

    # 1. Consultar Saldo Real Disponible y Pendiente (Balance API)
    balance_data = fetch_stripe_data("balance", api_key)
    if balance_data:
        if 'available' in balance_data:
            for item in balance_data['available']:
                amount = item['amount'] / 100.0
                currency = item['currency'].upper()
                log_message(f"   • Saldo Disponible en Stripe: {amount:.2f} {currency}")
        if 'pending' in balance_data:
            for item in balance_data['pending']:
                amount = item['amount'] / 100.0
                currency = item['currency'].upper()
                log_message(f"   • Saldo Pendiente en Stripe:  {amount:.2f} {currency}")

    # 2. Consultar Cargos Recientes (Charges API)
    charges_data = fetch_stripe_data("charges?limit=10", api_key)
    if charges_data and 'data' in charges_data:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Crear tabla de auditoría de eventos de Stripe si no existe
        cur.execute("""
        CREATE TABLE IF NOT EXISTS processed_stripe_events_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            event_type TEXT,
            amount_eur REAL,
            amount_usd REAL,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Inspeccionar columnas existentes en revenue_settlements
        cur.execute("PRAGMA table_info(revenue_settlements)")
        settlement_cols = [row[1] for row in cur.fetchall()]
        
        inserted_count = 0
        for charge in charges_data['data']:
            ch_id = charge['id']
            ch_amount = charge['amount'] / 100.0
            ch_currency = charge['currency'].upper()
            ch_status = charge['status']
            
            amount_eur = ch_amount if ch_currency == 'EUR' else round(ch_amount * 0.92, 2)
            amount_usd = ch_amount if ch_currency == 'USD' else round(ch_amount * 1.08, 2)
            
            if ch_status == 'succeeded':
                cur.execute("""
                    INSERT OR IGNORE INTO processed_stripe_events_v2 
                    (event_id, event_type, amount_eur, amount_usd, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (ch_id, 'charge.succeeded', amount_eur, amount_usd, 'PROCESSED'))
                
                # Insertar de forma adaptativa según el esquema real de revenue_settlements
                if 'amount_usd' in settlement_cols and 'status' in settlement_cols:
                    if 'client_id' in settlement_cols:
                        cur.execute("""
                            INSERT OR IGNORE INTO revenue_settlements (client_id, amount_usd, status)
                            VALUES (?, ?, 'COMPLETED')
                        """, (charge.get('customer', 'STRIPE_LIVE_CLIENT'), amount_usd))
                    else:
                        cur.execute("""
                            INSERT OR IGNORE INTO revenue_settlements (amount_usd, status)
                            VALUES (?, 'COMPLETED')
                        """, (amount_usd,))
                
                inserted_count += 1
                log_message(f"   • Cargo Detectado: {ch_id} | {ch_amount:.2f} {ch_currency} [{ch_status}] -> Registrado en DB.")
                
        conn.commit()
        conn.close()
        log_message(f"✅ Sincronización completada. {inserted_count} cargos importados desde Stripe.")

if __name__ == '__main__':
    run_stripe_sync()
