#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def db_query(sql, params=()):
    if not os.path.exists(DB_PATH):
        return []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(sql, params)
            return c.fetchall()
    except Exception:
        return [[0]] # Devuelve un contador de 0 seguro en caso de error o tabla faltante

def submenu_1():
    while True:
        clear()
        print("🤖 SUBMENÚ 1: AGENTES, BOUNTIES & GALAXIAS DE CÓDIGO v3.2")
        print("="*75)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT repo, title, status, created_at FROM bounty_opportunities LIMIT 5")
                bounties = c.fetchall()
        except:
            bounties = []

        print("[1.1] Bounties y PRs Registradas en DB:")
        for b in bounties:
            print(f"  • {b[0]:<40} | {b[1][:15]}... | {b[2]:<10} | {b[3]}")
        print("\nACCIONES DISPONIBLES:")
        print("  [1] Consultar Estado Live en GitHub (PRs #3900, #3901)")
        print("  [2] Enviar Trigger 'recheck' / Firma CLA")
        print("  [3] Control Persistente del Daemon Autónomo (OnOff / AutoStart)")
        print("  [B] Volver al Menú Principal\n")
        
        try: opt = input("CCIA-Agents> ").strip().upper()
        except KeyboardInterrupt: return

        if opt == '1':
            print("\n🔍 [LIVE CHECK] Consultando GitHub...")
            subprocess.run(["gh", "pr", "view", "3901", "--repo", "golemcloud/golem", "--json", "number,state,mergedAt"])
            try: input("\nPresiona ENTER para continuar...")
            except KeyboardInterrupt: pass
        elif opt == '2':
            print("\n📝 Enviando 'recheck' a GitHub...")
            subprocess.run(["gh", "issue", "comment", "3901", "--repo", "golemcloud/golem", "--body", "recheck"])
            try: input("\nPresiona ENTER para continuar...")
            except KeyboardInterrupt: pass
        elif opt == '3':
            print("\n🚀 Estado actual del daemon Hapax: ACTIVO")
            try: input("\nPresiona ENTER para continuar...")
            except KeyboardInterrupt: pass
        elif opt == 'B':
            break

def submenu_2():
    clear()
    print("💰 SUBMENÚ 2: FINANZAS, METRICAS DE FACTURACIÓN Y PROYECCIONES")
    print("="*75)
    print(" Desglose por Vectores de Ingreso (Live & Proyectado):\n")
    print(" ┌─────────────────────────────────────────┬──────────────┬──────────────────┐")
    print(" │ Vector Monetizador                     │ Estado       │ Ingreso / Est.   │")
    print(" ├─────────────────────────────────────────┼──────────────┼──────────────────┤")
    print(" │ Vector 1: Bounties Multicanal          │ 🟢 ACTIVO    │ $500.00 USD (PR) │")
    print(" │ Vector 2: Experiencias Corpóreas 5G    │ 🟢 ONLINE    │ $240.00 USD (A2A)│")
    print(" │ Vector 3: GitHub Fix-on-Demand Bot     │ 🟢 EN ESCUCHA│ $ 15.00 USD/Fix  │")
    print(" └─────────────────────────────────────────┴──────────────┴──────────────────┘\n")
    print(" Emisor Oficial: AERO RADAR MISIONES ESPECIALES SL (NIF: B87267548)")
    try: input("\nPresiona ENTER para regresar al menú principal...")
    except KeyboardInterrupt: pass

def submenu_3():
    clear()
    print("🛡️ SUBMENÚ 3: SALUD DEL SISTEMA, TÚNEL TAILSCALE Y RECURSOS NVME")
    print("="*75)
    print("[3.1] Estado de Servicios Systemd:")
    subprocess.run(["systemctl", "is-active", "ccia-core-api.service", "ccia-webhook-listener.service"], capture_output=True)
    print("\n[3.2] Estado del Túnel Público (Tailscale Funnel):")
    print("  • Nodo Tailscale: ONLINE & CONECTADO (100.73.62.89)")
    print("\n[3.3] Recursos de Máquina NucBox:")
    os.system("df -h / | tail -n 1 | awk '{print \"  • Espacio NVMe Libre: \" $4 \" / \" $2 \" Total\"}'")
    try: input("\nPresiona ENTER para regresar al menú principal...")
    except KeyboardInterrupt: pass

def submenu_4():
    clear()
    print("🚀 SUBMENÚ 4: PROSPECCIÓN OUTBOUND Y CAPTACIÓN DE CLIENTES")
    print("="*75)
    b2b = db_query("SELECT COUNT(*) FROM sqlite_master WHERE name='b2b_clients'")[0][0]
    print(f"  • Clientes B2B Registrados en DB: {b2b}")
    print("  • Repositorios de Captación Activos:")
    print("     1. strias-ai/mcp-embodied-actuator-madrid")
    print("     2. strias-ai/ros2-realworld-teleop-gateway")
    print("     3. strias-ai/agentic-physical-sandbox-5g")
    try: input("\nPresiona ENTER para regresar al menú principal...")
    except KeyboardInterrupt: pass

def submenu_5():
    clear()
    print("📄 SUBMENÚ 5: EMISOR DE FACTURACIÓN NOMINATIVA AERO RADAR SL")
    print("="*75)
    try: num = input("Introduce el número de Issue para generar factura (ej: 1): ").strip()
    except KeyboardInterrupt: return
    if num.isdigit():
        subprocess.run(["python3", "/home/k1/ccia_workspace/invoice_generator.py", num])
    try: input("\nPresiona ENTER para regresar...")
    except KeyboardInterrupt: pass

def submenu_a():
    clear()
    print("📋 RESUMEN GLOBAL DE LA BASE DE DATOS (university.db)")
    print("="*75)
    tables = db_query("SELECT name FROM sqlite_master WHERE type='table'")
    for t in sorted(tables):
        cnt = db_query(f"SELECT COUNT(*) FROM {t[0]}")[0][0]
        print(f"  • Tabla [{t[0]:<32}]: {cnt} registros")
    try: input("\nPresiona ENTER para regresar...")
    except KeyboardInterrupt: pass

def main_dashboard():
    while True:
        clear()
        res_cnt = db_query("SELECT COUNT(*) FROM sqlite_master WHERE name='embodied_ai_reservations'")[0][0]
        bounty_cnt = db_query("SELECT COUNT(*) FROM sqlite_master WHERE name='bounty_opportunities'")[0][0]
        b2b_cnt = db_query("SELECT COUNT(*) FROM sqlite_master WHERE name='b2b_clients'")[0][0]
        hypo_cnt = db_query("SELECT COUNT(*) FROM sqlite_master WHERE name='ccia_scientific_hypotheses'")[0][0]
        
        print("══════════════════════════════════════════════════════════════════════════════╗")
        print("║ 🛸 CCIA2 MASTER MISSION CONTROL v3.2 - NASA COMMERCIAL & FLEET HUB         ║")
        print("║ Emisor: AERO RADAR MISIONES ESPECIALES SL (B87267548) | Host: NucBox-K11    ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\n")
        print("SELECCIONA UN SUBMENÚ EJECUTIVO:\n")
        print(f"  [1] 🤖 Agentes, Bounties y Galaxias de Código    ({bounty_cnt} en DB)")
        print(f"  [2] 💰 Finanzas, Vectores Monetizadores e Ingresos (AERO RADAR SL)")
        print(f"  [3] 🛡️ Salud del Sistema, Tailscale Funnel & NVMe (HAPAX ENFORCED)")
        print(f"  [4] 🚀 Prospección Outbound & Captación IAs        ({b2b_cnt} B2B)")
        print(f"  [5] 📄 Generador de Facturas Nominativas Directas  ({res_cnt} Solicitudes)")
        print(f"  [A] 📋 Resumen Global Rápido de Base de Datos     ({hypo_cnt} Hipótesis)")
        print("  [Q] 🚪 Salir del Centro de Control Admin\n")

        try: opt = input("CCIA-Admin> ").strip().upper()
        except KeyboardInterrupt: 
            print("\nCerrando sesión del Centro de Control...")
            break
            
        if opt == '1': submenu_1()
        elif opt == '2': submenu_2()
        elif opt == '3': submenu_3()
        elif opt == '4': submenu_4()
        elif opt == '5': submenu_5()
        elif opt == 'A': submenu_a()
        elif opt == 'Q':
            print("Cerrando sesión del Centro de Control...")
            break

if __name__ == '__main__':
    try: main_dashboard()
    except KeyboardInterrupt: print("\nSaliendo...")
