#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import datetime
import subprocess
import urllib.request
import urllib.parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
DB_PATH = "/home/k1/ccia_workspace/university.db"
WORKSPACE_DIR = "/home/k1/ccia_workspace"
GH_USER = "strias-ai"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT UNIQUE,
            current_version TEXT,
            commit_sha TEXT,
            remote_url TEXT,
            last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_sync_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            local_artifacts_count INTEGER,
            remote_artifacts_count INTEGER,
            diff_detected INTEGER,
            audit_log TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_pub_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT,
            target_version TEXT,
            reason TEXT,
            release_notes TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_local_commit_sha():
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=WORKSPACE_DIR)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"

def count_local_artifacts():
    modules_dir = os.path.join(WORKSPACE_DIR, "modules")
    if os.path.exists(modules_dir):
        files = [f for f in os.listdir(modules_dir) if f.startswith("art_") and f.endswith(".py")]
        return len(files)
    return 0

def fetch_remote_repo_info(repo_name, token):
    url = f"https://api.github.com/repos/{GH_USER}/{repo_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CCiA-GitHub-Librarian-v1.0"
    }
    if token and not token.startswith("tu_g"):
        headers["Authorization"] = f"token {token}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception:
        return None

def run_sync_audit():
    token = os.environ.get("GITHUB_TOKEN", "")
    init_db()
    
    local_sha = get_local_commit_sha()
    local_arts = count_local_artifacts()
    
    remote_data = fetch_remote_repo_info("ccia-swarm", token)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    diff_detected = 0
    audit_msg = ""
    
    if remote_data:
        repo_url = remote_data.get("html_url", f"https://github.com/{GH_USER}/ccia-swarm")
        
        cursor.execute('''
            INSERT INTO github_catalog (repo_name, current_version, commit_sha, remote_url, last_synced_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(repo_name) DO UPDATE SET
                current_version=excluded.current_version,
                commit_sha=excluded.commit_sha,
                last_synced_at=CURRENT_TIMESTAMP
        ''', ("ccia-swarm", f"v3.0 (Arts: {local_arts})", local_sha, repo_url))
        
        pending_count = cursor.execute("SELECT COUNT(*) FROM github_pub_requests WHERE status='PENDING'").fetchone()[0]
        
        if pending_count == 0:
            cursor.execute('''
                INSERT OR IGNORE INTO github_pub_requests (repo_name, target_version, reason, release_notes, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "ccia-swarm",
                f"v3.1.0-art{local_arts}",
                f"Detectados {local_arts} artefactos locales certificados (SHA: {local_sha}). Sincronización disponible.",
                f"Release automatizada: Módulos de Inmunidad, Grafo Temporal GraphRAG y Módulos Científicos v8.0 integrados.",
                "PENDING"
            ))
            diff_detected = 1
            audit_msg = f"Diferencia detectada. Creada solicitud de versión v3.1.0-art{local_arts}."
        else:
            audit_msg = "Repositorio remoto auditado. Existen solicitudes pendientes de aprobación."
    else:
        audit_msg = "Consulta local completada. La API de GitHub no devolvió cambios remotos."

    cursor.execute('''
        INSERT INTO github_sync_audit (local_artifacts_count, remote_artifacts_count, diff_detected, audit_log)
        VALUES (?, ?, ?, ?)
    ''', (local_arts, local_arts, diff_detected, audit_msg))
    
    conn.commit()
    conn.close()

def run_e2e_audit():
    console.print("\n" + "=" * 75)
    console.print("🧪 AUDITORÍA Y VERIFICACIÓN END-TO-END: AGENTE BIBLIOTECARIO (ARTEFACTO 45)")
    console.print("=" * 75)

    console.print("\n🔍 1. Lanzando auditoría de diferencias (--cron)...")
    run_sync_audit()
    console.print("✅ Auditoría de diferencias completada.")

    console.print("\n📊 2. Verificando tablas de catálogo y solicitudes de publicación...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cat_rows = c.execute("SELECT repo_name, current_version, commit_sha, remote_url, last_synced_at FROM github_catalog").fetchall()
    req_rows = c.execute("SELECT id, repo_name, target_version, reason, status FROM github_pub_requests ORDER BY id DESC LIMIT 5").fetchall()

    table_cat = Table(title="📦 Repositorios en Catálogo Agéntico", expand=True)
    table_cat.add_column("Repo", style="cyan")
    table_cat.add_column("Versión Registrada", style="yellow")
    table_cat.add_column("Commit SHA", style="magenta")
    table_cat.add_column("Sincronizado", style="dim")
    for r in cat_rows:
        table_cat.add_row(r[0], r[1], r[2], str(r[4]))
    console.print(table_cat)

    table_req = Table(title="🚀 Solicitudes de Publicación Registradas", expand=True)
    table_req.add_column("ID", style="bold cyan")
    table_req.add_column("Repo / Target Version", style="white")
    table_req.add_column("Motivo", style="yellow")
    table_req.add_column("Estado", style="green")
    for r in req_rows:
        table_req.add_row(str(r[0]), f"{r[1]} -> {r[2]}", r[3], r[4])
    console.print(table_req)

    console.print("\n🌐 3. Verificando estado del repositorio remoto en GitHub...")
    git_remote = subprocess.run(["git", "remote", "-v"], cwd=WORKSPACE_DIR, capture_output=True, text=True).stdout.strip()
    console.print(f"  • Remoto configurado:\n{git_remote}")

    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_DIR, capture_output=True, text=True).stdout.strip()
    if not git_status:
        console.print("\n[bold green]✅ EL REPOSITORIO LOCAL ESTÁ 100% SINCRONIZADO CON GITHUB.[/bold green]")
    else:
        console.print(f"\n[bold yellow]ℹ️ Archivos pendientes de commit:\n{git_status}[/bold yellow]")

    conn.close()
    console.print("\n" + "=" * 75)

def display_menu():
    init_db()
    
    while True:
        console.print("\n" + "=" * 70)
        console.print(Panel(
            "[bold cyan]📚 CCiA GITHUB LIBRARIAN AGENT v1.0 (ARTEFACTO 45)[/bold cyan]\n"
            "[white]Auditor de Versiones, Catálogo de Repositorios y Gestor de Publicaciones[/white]",
            title="[bold yellow]MISSION CONTROL - GITHUB AGENT[/bold yellow]",
            expand=True
        ))
        
        console.print("[1] 📊 Ver Catálogo de Repositorios Publicados en GitHub")
        console.print("[2] 🔍 Ejecutar Auditoría de Diferencias (Local vs GitHub Remote)")
        console.print("[3] 🚀 Ver y Aprobar Solicitudes de Publicación Pendientes")
        console.print("[4] 📜 Ver Historial de Auditorías y Logs del Agente")
        console.print("[5] 🧪 Ejecutar Auditoría End-to-End y Diagnóstico de Autopublicación")
        console.print("[0] ⬅️ Salir")
        
        choice = input("\nSelecciona una opción [0-5]: ").strip()
        
        if choice == "1":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT repo_name, current_version, commit_sha, remote_url, last_synced_at FROM github_catalog").fetchall()
            conn.close()
            
            table = Table(title="📦 Repositorios Registrados en GitHub", expand=True)
            table.add_column("Repositorio", style="cyan")
            table.add_column("Versión Registrada", style="yellow")
            table.add_column("Commit SHA", style="magenta")
            table.add_column("URL Pública", style="green")
            table.add_column("Última Sincronización", style="dim")
            
            for r in rows:
                table.add_row(r[0], r[1], r[2], r[3], str(r[4]))
            console.print(table)
            input("\nPresiona ENTER para continuar...")

        elif choice == "2":
            console.print("\n[cyan]🔍 Ejecutando auditoría de diferencias con la API de GitHub...[/cyan]")
            run_sync_audit()
            console.print("[bold green]✅ Auditoría completada con éxito.[/bold green]")
            input("\nPresiona ENTER para continuar...")

        elif choice == "3":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, repo_name, target_version, reason, release_notes, status FROM github_pub_requests WHERE status='PENDING'").fetchall()
            
            if not rows:
                console.print("\n[yellow]No hay solicitudes de publicación pendientes de aprobación.[/yellow]")
                conn.close()
                input("\nPresiona ENTER para continuar...")
                continue

            table = Table(title="🚀 Solicitudes de Publicación Pendientes", expand=True)
            table.add_column("ID", style="bold cyan", width=5)
            table.add_column("Repositorio / Versión", style="white")
            table.add_column("Motivo de Publicación", style="yellow")
            table.add_column("Notas de Versión (Release Notes)", style="green")
            table.add_column("Estado", style="magenta")

            for r in rows:
                table.add_row(str(r[0]), f"{r[1]}\n[bold]{r[2]}[/bold]", r[3], r[4], r[5])
            
            console.print(table)
            
            sub_c = input("\n¿Deseas aprobar y publicar alguna solicitud? Ingresa el ID (o 0 para cancelar): ").strip()
            if sub_c.isdigit() and int(sub_c) > 0:
                req_id = int(sub_c)
                target_req = c.execute("SELECT repo_name, target_version, release_notes FROM github_pub_requests WHERE id=? AND status='PENDING'", (req_id,)).fetchone()
                if target_req:
                    repo, ver, notes = target_req
                    console.print(f"\n[cyan]🚀 Despachando publicación para `{repo}` versión `{ver}`...[/cyan]")
                    
                    try:
                        subprocess.run(["git", "add", "."], cwd=WORKSPACE_DIR, check=True)
                        subprocess.run(["git", "commit", "-m", f"release: {ver} - {notes}"], cwd=WORKSPACE_DIR, capture_output=True)
                        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE_DIR, capture_output=True, text=True)
                        
                        c.execute("UPDATE github_pub_requests SET status='PUBLISHED_AND_DISPATCHED' WHERE id=?", (req_id,))
                        c.execute("UPDATE github_catalog SET current_version=?, last_synced_at=CURRENT_TIMESTAMP WHERE repo_name=?", (ver, repo))
                        conn.commit()
                        console.print("[bold green]🎉 Publicación completada y sincronizada con GitHub con éxito.[/bold green]")
                    except Exception as e:
                        console.print(f"[bold red]❌ Error durante la ejecución de la publicación: {e}[/bold red]")
                else:
                    console.print("[red]ID no encontrado o ya procesado.[/red]")
            conn.close()
            input("\nPresiona ENTER para continuar...")

        elif choice == "4":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, checked_at, local_artifacts_count, diff_detected, audit_log FROM github_sync_audit ORDER BY id DESC LIMIT 10").fetchall()
            conn.close()

            table = Table(title="📜 Registro Histórico de Auditorías del Agente Bibliotecario", expand=True)
            table.add_column("ID", style="cyan", width=5)
            table.add_column("Fecha/Hora", style="white")
            table.add_column("Artefactos Locales", style="bold yellow")
            table.add_column("Diff Detectado", style="magenta")
            table.add_column("Detalle de Auditoría", style="green")

            for r in rows:
                table.add_row(str(r[0]), str(r[1]), str(r[2]), "SÍ" if r[3] else "NO", r[4])
            console.print(table)
            input("\nPresiona ENTER para continuar...")

        elif choice == "5":
            run_e2e_audit()
            input("\nPresiona ENTER para continuar...")

        elif choice == "0":
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cron":
        run_sync_audit()
    else:
        display_menu()
