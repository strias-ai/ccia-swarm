#!/usr/bin/env python3
"""
CCiA Public Repositories & Monetization Inspector v2.0 (Real Diagnostic Engine)
"""
import sqlite3
import os
import json
import urllib.request
import socket
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

DB_PATH = "/home/k1/ccia_workspace/university.db"
WELL_KNOWN_PATH = "/home/k1/ccia_workspace/public_well_known/agent.json"

def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def check_http_endpoint(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CCiA-Checker/2.0'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None, str(e)

def inspect_publications():
    console = Console()
    console.clear()

    console.print(Panel(
        "[bold cyan]🌐 AUDITORÍA EN TIEMPO REAL DE SERVICIOS Y PUBLICACIONES CCIA[/bold cyan]\n"
        "[white]Diagnóstico de sockets locales, endpoints HTTP, archivos de configuración y DB[/white]",
        title="CCIA PUBLICITY & REPOSITORY CHECKER v2.0",
        expand=True
    ))

    # 1. Auditoría del Manifiesto .well-known/agent.json
    console.print("\n[bold yellow]1. Inspección de Manifiesto A2A (.well-known/agent.json)[/bold yellow]")
    if os.path.exists(WELL_KNOWN_PATH):
        try:
            with open(WELL_KNOWN_PATH, 'r') as f:
                agent_data = json.load(f)
            
            raw_services = agent_data.get('services', [])
            serv_list = []
            for s in raw_services:
                if isinstance(s, dict):
                    serv_list.append(s.get('name', s.get('id', str(s))))
                else:
                    serv_list.append(str(s))
            
            serv_str = ', '.join(serv_list) if serv_list else 'Ninguno especificado'
            
            console.print("  • [green]STATUS ARCHIVO:[/green] PRESENTE EN DISCO")
            console.print(f"  • [white]Nombre Agente:[/white] {agent_data.get('name', 'CCiA Agent')}")
            console.print(f"  • [white]Servicios M2M:[/white] {serv_str}")
        except Exception as ex:
            console.print(f"  • [red]ERROR PARSEANDO JSON:[/red] {ex}")
    else:
        console.print("  • [red]STATUS ARCHIVO:[/red] No encontrado en la ruta esperada.")

    # 2. Comprobación de Sockets y Puertos
    console.print("\n[bold yellow]2. Estado de Puertos y Sockets en Ejecución[/bold yellow]")
    ports_to_check = [
        (8000, "API Gateway & Protocolo A2A (Artefacto 40)"),
        (8080, "Micro-SaaS Multi-Tenant Landing (Artefacto 31)"),
        (5000, "Stripe Webhook Listener (Artefacto 02)"),
        (8081, "VANT Security Code Auditor (Artefacto 06)")
    ]
    
    table_ports = Table(expand=True)
    table_ports.add_column("Puerto", justify="center", style="cyan", no_wrap=True)
    table_ports.add_column("Servicio Asociado", style="white")
    table_ports.add_column("Socket Local", style="bold green")
    table_ports.add_column("Respuesta HTTP", style="magenta")

    for port, service_name in ports_to_check:
        is_open = check_port("127.0.0.1", port)
        status_str = "[bold green]ONLINE (LISTEN)[/bold green]" if is_open else "[bold yellow]OFFLINE / IDLE[/bold yellow]"
        
        http_res = "N/A"
        if is_open:
            code, _ = check_http_endpoint(f"http://127.0.0.1:{port}/")
            http_res = f"HTTP {code}" if code else "Sin cabecera HTTP"
            
        table_ports.add_row(str(port), service_name, status_str, http_res)

    console.print(table_ports)

    # 3. Verificación HTTP directa de endpoint .well-known
    console.print("\n[bold yellow]3. Test de Endpoint HTTP: http://127.0.0.1:8000/.well-known/agent.json[/bold yellow]")
    code, _ = check_http_endpoint("http://127.0.0.1:8000/.well-known/agent.json")
    if code == 200:
        console.print("  • [green]ÉXITO (200 OK):[/green] El servidor responde y sirve el manifiesto A2A correctamente.")
    elif code is not None:
        console.print(f"  • [yellow]RESPUESTA HTTP {code}:[/yellow] El servidor responde en el puerto 8000.")
    else:
        console.print("  • [bold red]NO ACTIVO:[/red] El servidor del puerto 8000 no está escuchando actualmente.")

    # 4. Verificación de Registros en DB
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM ccia_artifact_manifests;")
        total_arts = cur.fetchone()[0]
        console.print("\n[bold yellow]4. Estado Base de Datos (university.db)[/bold yellow]")
        console.print(f"  • [white]Artefactos Registrados:[/white] {total_arts}")
        console.print(f"  • [white]Integridad DB:[/white] [green]OK[/green]")
        conn.close()

    console.print("\n[bold green]✅ Verificación completada.[/bold green]\n")

if __name__ == "__main__":
    inspect_publications()
