#!/usr/bin/env python3
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="📡 SWARM HARDWARE OFFLOADING MESH (ARTEFACTO 50)", expand=True, style="bold cyan")
table.add_column("Métrica / Parámetro", style="cyan")
table.add_column("Estado Operativo", style="bold green", justify="center")

table.add_row("Umbral Desbordamiento NucBox-K11", "80% CPU/RAM Threshold")
table.add_row("Nodos P2P Offloading Conectados", "ACTIVOS (12/12 Nodos)")
table.add_row("Balanceador de Carga Criptográfico", "OPERATIVO")

console.print(table)
