# -*- coding: utf-8 -*-
import sqlite3
import subprocess
import os

DB_PATH = "/home/k1/ccia_workspace/university.db"

def display_financial_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n" + "="*55)
    print(" 💳 RESUMEN FINANCIERO & CLIENTES SaaS (Stripe / API Keys)")
    print("="*55)
    cursor.execute("SELECT client_name, api_key, credits, total_requests FROM api_clients")
    rows = cursor.fetchall()
    if not rows:
        print(" No hay clientes registrados en api_clients.")
    for r in rows:
        print(f" • Cliente: {r[0]:<20} | Key: {r[1]:<20} | Créditos: {r[2]:<6} | Peticiones: {r[3]}")
    conn.close()

def display_broker_tickets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n" + "="*55)
    print(" 🎫 BROKER DE RECURSOS AGENTE <-> HUMANO (Tickets Pending)")
    print("="*55)
    cursor.execute("SELECT id, agent, resource, status, created_at FROM resource_tickets ORDER BY id DESC LIMIT 5")
    tickets = cursor.fetchall()
    if not tickets:
        print(" Sin tickets de recursos registrados.")
    for t in tickets:
        print(f" Ticket #{t[0]} | Agente: {t[1]:<12} | Recurso: {t[2]:<25} | Estado: {t[3]}")
    conn.close()

def display_vant_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n" + "="*55)
    print(" 🤖 TELEMETRÍA FLOTA MULTIAGENTE DOCKER VANT (5 Arquetipos)")
    print("="*55)
    cursor.execute("SELECT agent_name, action, status, timestamp FROM vant_agent_telemetry ORDER BY id DESC LIMIT 5")
    logs = cursor.fetchall()
    if not logs:
        print(" No hay registros de telemetría VANT recientes.")
    for l in logs:
        print(f" [{l[3]}] Agente: {l[0]:<12} | Acción: {l[1]:<20} | Estado: {l[2]}")
    conn.close()

def launch_daemon_manager():
    subprocess.call(["python3", "/home/k1/ccia_workspace/Proyecto_Multi-Archivo/ccia_dashboard.py"])
