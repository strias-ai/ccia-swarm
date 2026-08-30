# -*- coding: utf-8 -*-
import typer
import httpx
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="CLI SDK para API CCIA Backend")
console = Console()
BASE_URL = "http://127.0.0.1:8000"

@app.command()
def register(email: str, password: str):
    """Registra un nuevo usuario."""
    res = httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if res.status_code == 200:
        console.print(f"[bold green]Usuario {email} creado exitosamente.[/bold green]")
    else:
        console.print(f"[bold red]Error ({res.status_code}): {res.text}[/bold red]")

@app.command()
def login(email: str, password: str):
    """Inicia sesión y obtiene un Bearer Token."""
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code == 200:
        token = res.json()["access_token"]
        console.print(f"[bold green]Token obtenido:[/bold green]\n{token}")
    else:
        console.print(f"[bold red]Fallo de autenticación:[/bold red] {res.text}")

@app.command()
def list_items(token: str, skip: int = 0, limit: int = 10):
    """Lista elementos autenticados."""
    headers = {"Authorization": f"Bearer {token}"}
    res = httpx.get(f"{BASE_URL}/items/?skip={skip}&limit={limit}", headers=headers)
    if res.status_code == 200:
        items = res.json()
        table = Table(title="Elementos Registrados")
        table.add_column("ID", style="cyan")
        table.add_column("Título", style="magenta")
        table.add_column("Completado", style="green")
        
        for item in items:
            table.add_row(str(item["id"]), item["title"], str(item["completed"]))
        console.print(table)
    else:
        console.print(f"[bold red]Error ({res.status_code}): {res.text}[/bold red]")

if __name__ == "__main__":
    app()
