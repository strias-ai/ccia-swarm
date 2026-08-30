# -*- coding: utf-8 -*-
import sqlite3
import os
import sys
from rich.console import Console
from rich.table import Table
from study_session import run_autonomous_study_hour
from university_dean import UniversityDean
from telemetry_daemon import collect_metrics

console = Console()
DB_UNIV = os.path.join(os.path.dirname(__file__), "university.db")

def show_university_status():
    """Muestra los niveles de competencia de la flota y la biblioteca."""
    if not os.path.exists(DB_UNIV):
        console.print("[yellow]La base de datos de la universidad aún no tiene registros.[/yellow]")
        return
        
    conn = sqlite3.connect(DB_UNIV)
    cursor = conn.cursor()
    
    # 1. Niveles de los Agentes
    cursor.execute("SELECT agent_id, level, specialty, approved_count FROM agent_skills ORDER BY level DESC")
    skills = cursor.fetchall()
    
    if skills:
        t_skills = Table(title="🎖️ Nivel de Competencia y Progresión de los Agentes CCIA")
        t_skills.add_column("Agente", style="magenta")
        t_skills.add_column("Nivel", style="bold green", justify="center")
        t_skills.add_column("Especialidad Principal", style="yellow")
        t_skills.add_column("Tesis Aprobadas", style="cyan", justify="center")
        
        for s in skills:
            t_skills.add_row(s[0], f"Lvl {s[1]}", s[2], str(s[3]))
        console.print(t_skills)
        console.print("")

    # 2. Investigaciones en la Biblioteca
    cursor.execute("SELECT id, agent_id, topic, status, created_at FROM knowledge_vault ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    table = Table(title="🏛️ Biblioteca Universitaria CCIA (Últimas Investigaciones)")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Agente", style="magenta")
    table.add_column("Tema Investigado", style="yellow")
    table.add_column("Estado Decano", style="bold green")
    table.add_column("Fecha", style="blue")

    for r in rows:
        status_color = "green" if r[3] == "APPROVED" else "red"
        table.add_row(str(r[0]), r[1], r[2], f"[{status_color}]{r[3]}[/{status_color}]", str(r[4]))

    console.print(table)

def trigger_study_session():
    run_autonomous_study_hour()

def system_health_snapshot():
    m = collect_metrics()
    table = Table(title="🖥️ Telemetría en Tiempo Real (NucBox-K11)")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor Actual", style="bold green")
    
    table.add_row("Uso CPU", f"{m['cpu']}%")
    table.add_row("Uso RAM", f"{m['ram']}%")
    table.add_row("RAM Libre", f"{m['ram_available_mb']} MB")
    table.add_row("Ollama Engine", m['ollama'])
    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--univ":
            show_university_status()
        elif cmd == "--study":
            trigger_study_session()
        elif cmd == "--health":
            system_health_snapshot()
    else:
        system_health_snapshot()
        show_university_status()
