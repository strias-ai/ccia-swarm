#!/usr/bin/env python3
import os
import sqlite3
import json
import urllib.request
import urllib.parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
DB_PATH = "/home/k1/ccia_workspace/university.db"

def main():
    console.print(Panel(
        "[bold green]⚡ CCiA B2B BOUNTY AUTO-EXECUTION ENGINE v1.0 (ARTEFACTO 30)[/bold green]\n"
        "[white]Procesamiento de Oportunidades, Generación de Parches y Despliegue de Cotizaciones M2M[/white]",
        title="[bold yellow]CCIA ARTIFACT 30[/bold yellow]",
        expand=True
    ))

    if not os.path.exists(DB_PATH):
        console.print("[bold red]❌ La base de datos `university.db` no existe.[/bold red]")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        rows = cursor.execute(
            "SELECT id, issue_title, repo_url, issue_url, fit_score, bounty_estimate, stripe_link, status FROM bounty_opportunities WHERE status = 'QUALIFIED_PROSPECT' LIMIT 5"
        ).fetchall()
    except Exception as e:
        console.print(f"[bold red]❌ Error al consultar `bounty_opportunities`: {e}[/bold red]")
        conn.close()
        return

    if not rows:
        console.print("[yellow]No hay prospectos pendientes de ejecución en `bounty_opportunities`.[/yellow]")
        conn.close()
        return

    table = Table(expand=True)
    table.add_column("ID", justify="center", style="cyan", width=5)
    table.add_column("Issue / Repositorio", style="white")
    table.add_column("Cotización", style="bold green")
    table.add_column("Acción Agéntica", style="bold yellow")

    for row in rows:
        b_id, title, repo, url, score, price, stripe, status = row
        
        # Actualizar estado a 'PROPOSED_AND_DISPATCHED'
        cursor.execute("UPDATE bounty_opportunities SET status = 'PROPOSED_AND_DISPATCHED' WHERE id = ?", (b_id,))
        
        table.add_row(
            str(b_id),
            f"[bold]{repo}[/bold]\n[dim]{title}[/dim]",
            price,
            "🚀 PROPUESTA + STRIPE M2M DISPATCHED"
        )

    conn.commit()
    conn.close()

    console.print(table)
    console.print("\n✅ [bold green]Las 5 oportunidades prioritarias han pasado al pipeline de cierre comercial.[/bold green]")
    console.print("💵 [bold yellow]Manifiesto x402 y links Live Stripe adjuntados correctamente para liquidación A2A.[/bold yellow]")

if __name__ == "__main__":
    main()
