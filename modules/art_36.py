#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import datetime
import urllib.request
import urllib.parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bounty_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_title TEXT,
            repo_url TEXT,
            issue_url TEXT,
            bounty_estimate TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migración de esquema dinámica para añadir columnas si la tabla ya existía
    columns_to_add = [("fit_score", "INTEGER"), ("stripe_link", "TEXT")]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE bounty_opportunities ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

def calculate_ai_fit_score(title, body, labels):
    keywords = ["python", "security", "bug", "fix", "api", "jwt", "docker", "sqlite", "refactor", "auth"]
    text = (title + " " + (body or "") + " " + " ".join(labels)).lower()
    matches = sum(1 for kw in keywords if kw in text)
    score = min(99, 50 + (matches * 10))
    return score

def generate_stripe_quote(fit_score):
    if fit_score >= 80:
        return "$150.00 USD", "https://buy.stripe.com/live_bounty_high_tier"
    elif fit_score >= 60:
        return "$75.00 USD", "https://buy.stripe.com/live_bounty_mid_tier"
    else:
        return "$35.00 USD", "https://buy.stripe.com/live_bounty_std_tier"

def fetch_github_issues(token):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CCiA-Cognitive-Swarm-v3"
    }
    if token and not token.startswith("tu_g"):
        headers["Authorization"] = f"token {token}"
    
    raw_query = 'is:issue state:open label:bounty,bug,"help wanted",security'
    encoded_query = urllib.parse.quote(raw_query)
    url = f"https://api.github.com/search/issues?q={encoded_query}&sort=created&order=desc&per_page=10"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        console.print(f"[bold red]❌ Error HTTP {e.code} desde GitHub API: {e.reason}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]⚠️ Error de red/conexión: {e}[/bold red]")
        return []

def main():
    console.print(Panel(
        "[bold yellow]CCiA COGNITIVE OUTREACH & BOUNTY ENGINE v3.0 (I+D+i EDITION)[/bold yellow]\n"
        "[white]Búsqueda Avanzada, Scoring de Compatibilidad e Inyección de Links Live Stripe[/white]",
        title="[bold cyan]CCIA ARTIFACT 36[/bold cyan]",
        expand=True
    ))

    init_db()
    token = os.environ.get("GITHUB_TOKEN", "")

    if not token or token.startswith("tu_g"):
        console.print("[bold red]❌ GITHUB_TOKEN no válido en entorno.[/bold red]")
        return

    console.print("[cyan]🌐 Consultando API pública de GitHub...[/cyan]\n")
    items = fetch_github_issues(token)

    if not items:
        console.print("[yellow]No se obtuvieron resultados en esta consulta.[/yellow]")
        return

    table = Table(expand=True)
    table.add_column("Repositorio / Issue", style="cyan", width=35)
    table.add_column("Fit Score (IA)", justify="center", style="bold yellow")
    table.add_column("Cotización Live", style="green")
    table.add_column("Estado", style="magenta")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved_count = 0

    for item in items[:7]:
        repo_url = item.get("html_url", "").split("/issues/")[0]
        repo_name = "/".join(repo_url.split("/")[-2:])
        title = item.get("title", "")[:40]
        body = item.get("body", "")
        labels = [l.get("name", "") for l in item.get("labels", [])]
        issue_url = item.get("html_url", "")

        fit_score = calculate_ai_fit_score(title, body, labels)
        price_est, stripe_link = generate_stripe_quote(fit_score)

        cursor.execute(
            "INSERT INTO bounty_opportunities (issue_title, repo_url, issue_url, fit_score, bounty_estimate, stripe_link, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, repo_name, issue_url, fit_score, price_est, stripe_link, "QUALIFIED_PROSPECT")
        )
        saved_count += 1
        table.add_row(f"{repo_name}\n[dim]{title}[/dim]", f"{fit_score}%", price_est, "PROSPECTADO")

    conn.commit()
    conn.close()

    console.print(table)
    console.print(f"\n[bold green]🎯 {saved_count} oportunidades guardadas en `university.db` (Tabla: bounty_opportunities).[/bold green]")

if __name__ == "__main__":
    main()
