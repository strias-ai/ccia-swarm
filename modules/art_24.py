#!/usr/bin/env python3
import os
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

def main():
    console = Console()
    while True:
        console.clear()
        console.print(Panel(
            "[bold yellow]⚡ PANELES DE AUDITORÍA NIVEL DIOS (SUPER CTO / CEO & FINOPS)[/bold yellow]\n"
            "[white]Verificación global de monetización, seguridad, recursos y salud de servicios[/white]",
            title="[bold cyan]CCIA GOD MODE CONTROL PANEL v2.3[/bold cyan]",
            expand=True
        ))

        table = Table(expand=True)
        table.add_column("Opción", justify="center", style="cyan", width=10)
        table.add_column("Panel de Verificación / Auditoría", style="white")
        table.add_column("Área de Control", style="bold green")

        table.add_row("[1]", "🌐 CCiA Publicity & Repository Checker v2.3", "A2A & Tailscale Endpoints")
        table.add_row("[2]", "🛡️ Read-Only System Security & Audit Sentinel", "Inmunidad & Código Core")
        table.add_row("[3]", "💰 FinOps Cloud Auditor & Profitability Governor", "Control Financiero & Costes")
  [4] 🚀 Lanzar Panel de Mando y Control del Agente (art_45.py)
        table.add_row("[4]", "⚡ System Health Watchdog & Daemon Supervisor", "Puertos, Process & Memory")
        table.add_row("[5]", "💵 A2A Revenue Settlement & Escrow Monitor", "Liquidación de Transacciones")
        table.add_row("[6]", "🔬 Scientific Discovery & GraphRAG Memory", "I+D & Memoria Temporal")
        table.add_row("[7]", "🎯 Full Ecosystem Verification & Certifier", "Certificación Integral DB")
        table.add_row("[0]", "⬅️ Volver al Menú Principal Mission Control", "Navegación")

        console.print(table)
        opt = console.input("\n[bold yellow]Selecciona una opción [0-7]: [/bold yellow]").strip()

        modules_map = {
            "1": "/home/k1/ccia_workspace/modules/ccia_pub_checker.py",
            "2": "/home/k1/ccia_workspace/modules/ccia_readonly_audit.py",
            "3": "/home/k1/ccia_workspace/modules/finops_cloud_auditor.py",
            "4": "/home/k1/ccia_workspace/modules/system_health_watchdog.py",
            "5": "/home/k1/ccia_workspace/modules/a2a_revenue_settlement.py",
            "6": "/home/k1/ccia_workspace/modules/ccia_science_discovery.py",
            "7": "/home/k1/ccia_workspace/api_backend_jwt/verify_full_ecosystem.py"
        }

        if opt == "0" or opt == "":
            break
        elif opt in modules_map:
            script_path = modules_map[opt]
            if not os.path.exists(script_path):
                alt_path = script_path.replace("ccia_readonly_audit.py", "read_only_system_audit.py").replace("finops_cloud_auditor.py", "finops_auditor.py")
                if os.path.exists(alt_path):
                    script_path = alt_path

            if os.path.exists(script_path):
                console.clear()
                subprocess.run(["python3", script_path])
                console.input("\n[bold cyan]Presiona ENTER para volver al Submenú Nivel Dios...[/bold cyan]")
            else:
                console.print(f"[bold red]❌ El script {script_path} no se encuentra disponible en disco.[/bold red]")
                console.input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    main()
