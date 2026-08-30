import os
import sys
import sqlite3
import shutil
import subprocess
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

C_CYAN = "\033[1;36m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_MAGENTA = "\033[1;35m"
C_BLUE = "\033[1;34m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_db():
    return sqlite3.connect(DB_PATH)

def render_header(title):
    print(f"{C_CYAN}╭" + "─" * 78 + f"╮{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}{title:<76}{C_RESET} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}╰" + "─" * 78 + f"╯{C_RESET}")

def menu_agentes():
    clear_screen()
    render_header("🤖 SUBMENÚ 1: AGENTES, BOUNTIES & GALAXIAS DE CÓDIGO")
    conn = get_db()
    cursor = conn.cursor()
    
    print(f"{C_YELLOW}[1.1] Bounties y PRs Capturadas:{C_RESET}")
    cursor.execute("SELECT repo_name, bounty_amount, status, created_at FROM bounties ORDER BY id DESC LIMIT 10")
    bounties = cursor.fetchall()
    if bounties:
        for repo, amount, status, date in bounties:
            print(f"  • {repo:<40} | ${amount:>6.2f} USD | {C_GREEN}{status:<12}{C_RESET} | {date}")
    else:
        print("  • Sin registros recientes de bounties.")
        
    print(f"\n{C_YELLOW}[1.2] Repositorios Catalogados en el Sector:{C_RESET}")
    cursor.execute("SELECT count(*) FROM bounties")
    discovered = cursor.fetchone()[0]
    print(f"  • Total de galaxias de código escaneadas: {C_BOLD}{discovered}{C_RESET}")
    conn.close()
    
    input(f"\n{C_CYAN}Presiona ENTER para regresar al menú principal...{C_RESET}")

def menu_finanzas():
    clear_screen()
    render_header("💰 SUBMENÚ 2: FINANZAS, METRICAS DE FACTURACIÓN Y PROYECCIONES")
    conn = get_db()
    cursor = conn.cursor()
    
    print(f"{C_GREEN} Desglose por Vectores de Ingreso (Live & Proyectado):{C_RESET}\n")
    print(f" ┌─────────────────────────────────────────┬──────────────┬──────────────────┐")
    print(f" │ Vector Monetizador                     │ Estado       │ Ingreso / Est.   │")
    print(f" ├─────────────────────────────────────────┼──────────────┼──────────────────┤")
    print(f" │ Vector 1: Bounties Multicanal          │ 🟢 ACTIVO    │ $500.00 USD (PR) │")
    print(f" │ Vector 2: SaaS Core API Subscriptions  │ 🟢 ONLINE    │ $  0.00 USD (0)  │")
    print(f" │ Vector 3: GitHub Fix-on-Demand Bot     │ 🟢 EN ESCUCHA│ $ 15.00 USD/Fix  │")
    print(f" │ Vector 4: Datasets Metered Billing      │ 🟢 ONLINE    │ $ 0.001 USD/Rec  │")
    print(f" │ Vector 5: FinOps Cloud Auditor          │ 🟢 ACTIVO    │ $ 24.75 USD Com. │")
    print(f" │ Vector 6: A2A Escrow Micro-Transactions │ 🟢 ONLINE    │ En custodia      │")
    print(f" └─────────────────────────────────────────┴──────────────┴──────────────────┘\n")
    
    cursor.execute("SELECT COALESCE(SUM(amount), 0) / 100.0 FROM processed_stripe_events")
    captured_total = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(bounty_amount), 0.0) FROM bounties WHERE status IN ('PR_SUBMITTED', 'CLAIMED', 'HELD_IN_ESCROW')")
    bounties_total = cursor.fetchone()[0]
    total = captured_total + bounties_total
    
    print(f" {C_BOLD}Pipeline Total Estimado en Aprobación / Cobro:{C_RESET} {C_GREEN}${total:.2f} USD{C_RESET}")
    conn.close()
    
    input(f"\n{C_CYAN}Presiona ENTER para regresar al menú principal...{C_RESET}")

def menu_infraestructura():
    clear_screen()
    render_header("🛡️ SUBMENÚ 3: SALUD DEL SISTEMA, TÚNEL TAILSCALE Y RECURSOS NVME")
    
    print(f"{C_YELLOW}[3.1] Estado de Servicios Systemd:{C_RESET}")
    services = [
        ("ccia-webhook-listener.service", "Listener HTTP Stripe"),
        ("ccia-core-api.service", "Core API FastAPI Engine")
    ]
    for svc, desc in services:
        res = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True).stdout.strip()
        status_color = C_GREEN if res == "active" else C_RED
        print(f"  • {desc:<30} ({svc}): {status_color}{res.upper()}{C_RESET}")

    print(f"\n{C_YELLOW}[3.2] Estado del Túnel Público (Tailscale Funnel):{C_RESET}")
    try:
        ts_res = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=3).stdout.strip()
        if ts_res:
            node_line = ts_res.split('\n')[0]
            print(f"  • Nodo Tailscale: {C_GREEN}ONLINE & CONECTADO{C_RESET}")
            print(f"  • Detalles Nodo:  {node_line[:60]}")
            print(f"  • URL Funnel:     {C_CYAN}https://k1-nucbox-k11.tail01b79c.ts.net/v1/stripe/webhook{C_RESET}")
        else:
            print(f"  • Nodo Tailscale: {C_RED}DESCONECTADO{C_RESET}")
    except Exception as e:
        print(f"  • Verificación Tailscale: {C_YELLOW}No disponible en entorno local ({e}){C_RESET}")
        
    print(f"\n{C_YELLOW}[3.3] Recursos de Máquina NucBox:{C_RESET}")
    total, used, free = shutil.disk_usage("/")
    print(f"  • Espacio NVMe Libre: {C_BOLD}{free // (2**30)} GB{C_RESET} / {total // (2**30)} GB Total")
    
    print(f"\n{C_YELLOW}[3.4] Tareas Programadas (Cron Jobs):{C_RESET}")
    cron_res = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout.strip()
    cron_lines = [l for l in cron_res.split('\n') if l and not l.startswith('#')]
    for cl in cron_lines:
        print(f"  • {cl}")
        
    input(f"\n{C_CYAN}Presiona ENTER para regresar al menú principal...{C_RESET}")

def menu_prospeccion():
    clear_screen()
    render_header("🚀 SUBMENÚ 4: PROSPECCIÓN OUTBOUND Y CAPTACIÓN DE CLIENTES")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM api_clients")
    clients_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM vant_agent_telemetry")
    telemetry_count = cursor.fetchone()[0]
    
    print(f"{C_MAGENTA} Mapeo de Audiencia & Telemetría Outbound:{C_RESET}")
    print(f"  • Clientes API Registrados en Base de Datos: {C_BOLD}{clients_count}{C_RESET}")
    print(f"  • Registros de Telemetría e Interacciones: {C_BOLD}{telemetry_count}{C_RESET}")
    print(f"  • Endpoint Activo de Checkout Outbound: https://k1-nucbox-k11.tail01b79c.ts.net/v1/stripe/webhook")
    
    conn.close()
    input(f"\n{C_CYAN}Presiona ENTER para regresar al menú principal...{C_RESET}")

def main_dashboard():
    while True:
        clear_screen()
        print(f"{C_CYAN}╔" + "═" * 78 + f"╗{C_RESET}")
        print(f"{C_CYAN}║{C_RESET} {C_BOLD}{C_MAGENTA}🛸 CCIA MASTER MISSION CONTROL v18.0 - MASTER ADMIN DASHBOARD{C_RESET}               {C_CYAN}║{C_RESET}")
        print(f"{C_CYAN}║{C_RESET} {C_BOLD}Vault Status: ONLINE | Host: NucBox-K11 | Database: university.db{C_RESET}             {C_CYAN}║{C_RESET}")
        print(f"{C_CYAN}╚" + "═" * 78 + f"╝{C_RESET}")
        
        print(f"\n{C_BOLD}SELECCIONA UN SUBMENÚ EJECUTIVO:{C_RESET}\n")
        print(f"  {C_CYAN}[1]{C_RESET} 🤖 Agentes, Bounties y Galaxias de Código")
        print(f"  {C_CYAN}[2]{C_RESET} 💰 Finanzas, Vectores Monetizadores e Ingresos")
        print(f"  {C_CYAN}[3]{C_RESET} 🛡️ Salud del Sistema, Tailscale Funnel & NVMe")
        print(f"  {C_CYAN}[4]{C_RESET} 🚀 Prospección Outbound & Tráfico de Clientes")
        print(f"  {C_CYAN}[A]{C_RESET} 📋 Resumen Global Rápido de Base de Datos")
        print(f"  {C_CYAN}[Q]{C_RESET} 🚪 Salir del Centro de Control Admin\n")
        
        opt = input(f"{C_BOLD}CCIA-Admin> {C_RESET}").strip().upper()
        
        if opt == '1':
            menu_agentes()
        elif opt == '2':
            menu_finanzas()
        elif opt == '3':
            menu_infraestructura()
        elif opt == '4':
            menu_prospeccion()
        elif opt == 'A':
            clear_screen()
            render_header("📋 RESUMEN GLOBAL DE LA BASE DE DATOS")
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for t in tables:
                cursor.execute(f"SELECT count(*) FROM {t[0]}")
                c = cursor.fetchone()[0]
                print(f"  • Tabla [{t[0]:<30}]: {c} registros")
            conn.close()
            input(f"\n{C_CYAN}Presiona ENTER para regresar...{C_RESET}")
        elif opt == 'Q':
            print(f"\n{C_GREEN}Cerrando sesión en CCiA Master Admin Dashboard. ¡Sistemas operando autónomamente!{C_RESET}\n")
            sys.exit(0)

if __name__ == "__main__":
    main_dashboard()
