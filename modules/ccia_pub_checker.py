#!/usr/bin/env python3
"""
CCiA Public Repositories & Monetization Inspector v2.3
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

def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def check_http_endpoint(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CCiA-Checker/2.3'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None, str(e)

def inspect_publications():
    console = Console()
    console.clear()

    console.print(Panel(
        "[bold cyan]🌐 AUDITORÍA DE MONETIZACIÓN Y PUBLICACIÓN EXTERNA CCIA[/bold cyan]\n"
        "[white]Verificando Gateway A2A, URLs públicas Tailscale y manifiesto de servicios[/white]",
        title="CCIA PUBLICITY & REPOSITORY CHECKER v2.3",
        expand=True
    ))

    # 1. Verificación del Endpoint HTTP local y remoto
    console.print("\n[bold yellow]1. Endpoint HTTP A2A (http://127.0.0.1:8000/.well-known/agent.json)[/bold yellow]")
    code, body = check_http_endpoint("http://127.0.0.1:8000/.well-known/agent.json")
    if code == 200:
        console.print("  • [bold green]ESTADO HTTP:[/bold green] 200 OK (Servidor Escuchando)")
        try:
            data = json.loads(body)
            console.print(f"  • [white]Nombre Agente:[/white] {data.get('name')}")
            console.print(f"  • [white]Esquema Protocolo:[/white] {data.get('schema_version')}")
            console.print(f"  • [white]Base URL Pública:[/white] [cyan]{data.get('endpoints', {}).get('base_url')}[/cyan]")
            console.print(f"  • [white]Pasarelas Pago:[/white] {', '.join(data.get('monetization', {}).get('payment_rails', []))}")
            
            services = data.get('services', [])
            console.print("\n  [bold cyan]Servicios Monetizables Activos:[/bold cyan]")
            for s in services:
                if isinstance(s, dict):
                    console.print(f"    - [bold white]{s.get('id'):<18}[/bold white] | Precio: [green]{s.get('price'):<10}[/green] | Unidad: {s.get('unit')}")
                else:
                    console.print(f"    - {s}")
        except Exception as ex:
            console.print(f"  • [bold red]Error al decodificar JSON:[/bold red] {ex}")
    else:
        console.print(f"  • [bold red]ERROR HTTP {code}:[/bold red] {body}")

    # 2. Puertos de Servicios
    console.print("\n[bold yellow]2. Estado de Puertos en Escucha[/bold yellow]")
    ports = [(8000, "API Gateway / A2A Protocol"), (8080, "Micro-SaaS & Webhooks"), (5000, "Stripe Webhooks"), (8081, "VANT Auditor")]
    
    table = Table(expand=True)
    table.add_column("Puerto", justify="center", style="cyan")
    table.add_column("Servicio", style="white")
    table.add_column("Estado Socket", style="bold green")

    for p, sname in ports:
        st = "[bold green]ONLINE (LISTEN)[/bold green]" if check_port("127.0.0.1", p) else "[bold yellow]OFFLINE[/bold yellow]"
        table.add_row(str(p), sname, st)

    console.print(table)
    console.print("\n[bold green]✅ Verificación de publicación externa completada con éxito.[/bold green]\n")

if __name__ == "__main__":
    inspect_publications()
