#!/usr/bin/env python3
"""
CCiA Master Control Panel v18.1 - Dynamic All Artifacts Renderer
"""
import sqlite3
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

DB_PATH = "/home/k1/ccia_workspace/university.db"

def show_mission_control():
    console = Console()
    if not os.path.exists(DB_PATH):
        console.print("[red]❌ Base de datos university.db no encontrada.[/red]")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT artifact_id, name, version, category 
        FROM ccia_artifact_manifests 
        ORDER BY CAST(artifact_id AS INTEGER) ASC;
    """)
    rows = cur.fetchall()
    conn.close()

    header_panel = Panel(
        "[bold cyan]🛸 CCIA MISSION CONTROL v18.1 (SUPER ADMIN & GEMINISUPERCTO INTEGRATED)[/bold cyan]\n"
        "[white]Vault Status: ONLINE | DB Registry: university.db (ccia_artifact_manifests)[/white]",
        title="CENTRO DE MANDO Y CONTROL CERTIFICADO",
        expand=True
    )

    table = Table(title="📋 ARTEFACTOS Y PROYECTOS CERTIFICADOS (AUTO-DESCUBIERTOS DESDE DB)", expand=True)
    table.add_column("Opción", justify="center", style="cyan", no_wrap=True)
    table.add_column("Artefacto / Proyecto", style="bold white")
    table.add_column("Versión", justify="center", style="green")
    table.add_column("Categoría Operativa", style="magenta")

    for r in rows:
        aid = f"[{int(r[0])}]"
        name = str(r[1])
        ver = str(r[2]) if str(r[2]).startswith("v") else f"v{r[2]}"
        cat = str(r[3])
        table.add_row(aid, name, ver, cat)

    console.clear()
    console.print(header_panel)
    console.print(table)
    console.print("\n[bold yellow]Opciones Globales:[/bold yellow] [A] Resumen DB | [D] Docker Status | [Q] Salir\n")

if __name__ == "__main__":
    show_mission_control()
