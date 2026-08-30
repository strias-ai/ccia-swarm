# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
import time
import re

DB_PATH = '/home/k1/ccia_workspace/university.db'

def run_deployer():
    print("\n🚀 [CCiA Artifact 31] Micro-SaaS Auto-Deployer Engine v1.0.0")
    print("──────────────────────────────────────────────────────────────")
    
    raw_input = input("👉 Ingrese nombre o subdominio del cliente (ej: empresa1, cliente-b2b): ").strip()
    
    clean_slug = re.sub(r'https?://', '', raw_input)
    clean_slug = clean_slug.split('/')[0].split('.')[0].lower()
    if not clean_slug or clean_slug == 'k1-nucbox-k11':
        clean_slug = f"tenant-{int(time.time())}"
    
    full_domain = f"{clean_slug}.ccia-saas.com"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT tenant_id, company_name, status FROM microsaas_tenants WHERE domain = ?", (full_domain,))
    row = cur.fetchone()
    
    if row:
        print(f"\n⚠️ El tenant '{row[1]}' ({full_domain}) ya existe (ID: {row[0]}, Estado: {row[2]}).")
    else:
        cur.execute("""
            INSERT INTO microsaas_tenants (company_name, domain, plan, stripe_subscription_id, status)
            VALUES (?, ?, ?, ?, ?)
        """, (clean_slug.capitalize(), full_domain, 'ENTERPRISE_AST', f'sub_live_{int(time.time())}', 'ACTIVE'))
        
        conn.commit()
        print(f"\n✅ Nuevo Tenant Micro-SaaS registrado exitosamente:")
        print(f"   • Cliente: {clean_slug.capitalize()}")
        print(f"   • Dominio Asignado: https://{full_domain}")
        print(f"   • Plan: ENTERPRISE_AST")
        print(f"   • Endpoint Webhook Local: https://k1-nucbox-k11.tail01b79c.ts.net/v1/stripe/webhook")
        print(f"   • Estado: ACTIVE")
    
    conn.close()

if __name__ == '__main__':
    run_deployer()
