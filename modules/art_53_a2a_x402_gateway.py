#!/usr/bin/env python3
"""
Artefacto 53: CCiA Real A2A Gateway (Solana & Ethereum Native)
Conexión directa a monederos Bitpanda (Santiago Trias Gonzalez)
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def load_env_file():
    env_path = "/home/k1/ccia_workspace/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

def main():
    os.system('clear')
    load_env_file()
    
    sol_addr = os.environ.get("SOLANA_WALLET_ADDRESS", "NO_CONFIGURADA")
    eth_addr = os.environ.get("ETHEREUM_WALLET_ADDRESS", "NO_CONFIGURADA")
    host = os.environ.get("CRYPTO_HOST", "Bitpanda")
    beneficiary = os.environ.get("BENEFICIARY_NAME", "Santiago Trias Gonzalez")
    
    console.print(Panel.fit(
        "[bold green]⚡ CCiA AGENT-TO-AGENT (A2A) BITPANDA GATEWAY[/bold green]\n"
        "[bold white]Monetización Directa en Redes Solana & Ethereum[/bold white]",
        border_style="cyan"
    ))
    
    table = Table(expand=True)
    table.add_column("Canal / Monedero", style="cyan")
    table.add_column("Dirección de Recepción Directa", style="bold green", justify="center")
    table.add_column("Host / Plataforma", style="bold white", justify="center")
    
    table.add_row("Solana (SOL / SPL Tokens)", sol_addr, f"{host} ({beneficiary})")
    table.add_row("Ethereum (ETH / ERC-20)", eth_addr, f"{host} ({beneficiary})")
    table.add_row("Protocolo A2A Inter-Agent", "HTTP 402 / Native Crypto Transfers", "CCiA Core")
    
    console.print(table)
    
    print("\n[Estado de Operación A2A Real]:")
    print(f" ├─ Los agentes externos pueden emitir micropagos a la red Solana: {sol_addr[:8]}...{sol_addr[-6:]}")
    print(f" ├─ O a la red Ethereum: {eth_addr[:8]}...{eth_addr[-6:]}")
    print(f" └─ Fondos acreditados directamente en tu cuenta de {host}.")
    
    input("\nPresiona ENTER para regresar...")

if __name__ == "__main__":
    main()
