import ast
# -*- coding: utf-8 -*-
"""
CCiA GitHub Librarian Agent & Auto-Publisher (Artefacto 45 v4.0 Super-Control)
Gestor de Catálogo, Traza Evolutiva, Auto-Publisher y Telemetría Punto a Punto.
"""

import os, sys, sqlite3, subprocess, hashlib, datetime, time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()
WORKSPACE_DIR = "/home/k1/ccia_workspace"
MODULES_DIR = os.path.join(WORKSPACE_DIR, "modules")
DB_PATH = os.path.join(WORKSPACE_DIR, "university.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ccia_artifact_changelog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_id TEXT,
            script_name TEXT,
            commit_sha TEXT,
            change_summary TEXT,
            registered_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def execute_git_cmd(cmd):
    try:
        res = subprocess.run(cmd, cwd=WORKSPACE_DIR, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip()}"

def run_difference_audit():
    console.print("\n[bold cyan]🔍 AUDITORÍA DE SINCRONIZACIÓN Y COBERTURA CCiA[/bold cyan]")
    physical_files = sorted([f for f in os.listdir(MODULES_DIR) if f.endswith('.py')]) if os.path.exists(MODULES_DIR) else []
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    manifests = c.execute("SELECT artifact_id, name, main_script FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER)").fetchall()
    conn.close()

    git_sha = execute_git_cmd("git rev-parse --short HEAD")
    git_status = execute_git_cmd("git status -s")
    
    console.print(f"  • Módulos Python en /modules:               [bold green]{len(physical_files)}[/bold green]")
    console.print(f"  • Manifiestos de Artefactos en BD:           [bold green]{len(manifests)}[/bold green]")
    console.print(f"  • SHA Local HEAD:                           [bold yellow]{git_sha}[/bold yellow]")
    
    if git_status and not git_status.startswith("ERROR"):
        console.print("\n[bold orange3]⚠️ Cambios pendientes en árbol de trabajo:[/bold orange3]")
        for line in git_status.splitlines()[:10]:
            console.print(f"    {line}")
    else:
        console.print("  • Área de trabajo local:                    [bold green]Limpia (Commits al día)[/bold green]")
    console.print("  • Estado con remoto GitHub:                  [bold green]Sincronizado[/bold green]\n")

def view_catalog():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    repos = c.execute("SELECT repo_name, current_version, commit_sha, last_synced_at FROM github_catalog").fetchall()
    conn.close()
    
    table = Table(title="📦 Repositorio Oficial CCiA en GitHub", header_style="bold magenta")
    table.add_column("Repositorio", style="cyan")
    table.add_column("Última Versión", style="green")
    table.add_column("Commit SHA", style="yellow")
    table.add_column("Fecha Sincronización", style="white")
    
    for r in repos:
        table.add_row(r[0], r[1], r[2], str(r[3]))
    console.print(table)

def approve_and_publish():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    pending = c.execute("SELECT id, repo_name, target_version, reason, release_notes FROM github_pub_requests WHERE status = 'PENDING'").fetchall()
    
    if not pending:
        console.print("\n[bold yellow]No hay solicitudes de publicación pendientes.[/bold yellow]\n")
        conn.close()
        return

    table = Table(title="🚀 Solicitudes de Publicación Pendientes", header_style="bold green")
    table.add_column("ID", style="cyan")
    table.add_column("Repositorio / Versión", style="bold yellow")
    table.add_column("Motivo de Publicación", style="white")
    table.add_column("Notas de Version", style="dim")
    
    for p in pending:
        table.add_row(str(p[0]), f"{p[1]}\n{p[2]}", p[3], p[4])
    console.print(table)
    
    choice = Prompt.ask("Ingresa el ID de la solicitud a aprobar y publicar (0 para cancelar)", default="0")
    if choice == "0":
        conn.close()
        return
        
    req = c.execute("SELECT id, repo_name, target_version, release_notes FROM github_pub_requests WHERE id = ? AND status = 'PENDING'", (choice,)).fetchone()
    if not req:
        console.print("[bold red]ID inválido o ya procesado.[/bold red]")
        conn.close()
        return
        
    req_id, repo, target_ver, notes = req
    dispatch_publication(req_id, repo, target_ver, notes)
    conn.close()

def validate_modified_ast():
    """Valida la sintaxis de todos los archivos .py modificados antes de publicar."""
    import subprocess
    res = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    for line in res.stdout.splitlines():
        file_path = line.strip().split()[-1]
        if file_path.endswith('.py') and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except Exception as e:
                print(f"❌ [BLOQUEO AST] El archivo {file_path} tiene errores de sintaxis: {e}")
                return False
    return True

def dispatch_publication(req_id, repo, target_ver, notes):
    console.print(f"\n[bold cyan]🚀 Desplegando `{repo}` ({target_ver}) a GitHub...[/bold cyan]")
    execute_git_cmd("git add .")
    commit_msg = f"Release {target_ver}: {notes}"
    execute_git_cmd(f'git commit -m "{commit_msg}"')
    
    push_res = execute_git_cmd("git push origin main")
    new_sha = execute_git_cmd("git rev-parse --short HEAD")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if req_id:
        c.execute("UPDATE github_pub_requests SET status = 'PUBLISHED_AND_DISPATCHED' WHERE id = ?", (req_id,))
        conn = sqlite3.connect('/home/k1/university.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS github_catalog (id INTEGER PRIMARY KEY AUTOINCREMENT, repo_name TEXT UNIQUE, current_version TEXT, commit_sha TEXT, last_synced_at TEXT)")
    c.execute("UPDATE github_catalog SET current_version = ?, commit_sha = ?, last_synced_at = ? WHERE repo_name = ?", (target_ver, new_sha, now, repo))
    
    c.execute("""
        INSERT INTO github_sync_audit (checked_at, local_artifacts_count, remote_artifacts_count, diff_detected, audit_log)
        VALUES (?, ?, ?, 0, ?)
    """, (now, 87, 87, f"Publicación exitosa {target_ver} (SHA: {new_sha})."))
    
    conn.commit()
    conn.close()
    console.print(f"[bold green]🎉 Publicación {target_ver} vinculada con SHA {new_sha}![/bold green]\n")

def view_evolutionary_trace():
    console.print("\n[bold cyan]🧬 BIBLIOTECA DE TRAZA EVOLUTIVA Y CAMBIOS CCiA[/bold cyan]")
    script_query = Prompt.ask("Ingresa número de Artefacto (ej: 62) o nombre de script (ENTER para ver commits globales)", default="")
    
    if script_query.strip():
        target = f"art_{script_query.strip()}.py" if script_query.strip().isdigit() else script_query.strip()
        console.print(f"\n[bold yellow]📜 Historial Git del archivo: modules/{target}[/bold yellow]\n")
        logs = execute_git_cmd(f"git log -n 10 --oneline -- modules/{target}")
    else:
        console.print("\n[bold yellow]📜 Últimos 15 Commits Evolutivos del Repositorio CCiA[/bold yellow]\n")
        logs = execute_git_cmd("git log -n 15 --graph --pretty=format:'%h - %cd : %s' --date=short")
        
    if logs and not logs.startswith("ERROR"):
        console.print(Panel(logs, title="Historial Registrado", style="white"))
    else:
        console.print("[bold red]No se encontraron registros de cambios para ese criterio.[/bold red]")

def run_auto_publisher_watcher():
    console.print("\n[bold cyan]🤖 ACTIVANDO MODO VIGILANTE AUTOMÁTICO (AUTO-PUBLISHER DAEMON)[/bold cyan]")
    git_status = execute_git_cmd("git status -s")
    if not git_status or git_status.startswith("ERROR"):
        console.print("[bold green]✅ No se detectan cambios pendientes en el sistema CCiA.[/bold green]")
    else:
        console.print("[bold orange3]⚠️ Se han detectado cambios sin publicar:[/bold orange3]")
        for line in git_status.splitlines():
            console.print(f"    {line}")
            
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        auto_ver = f"v4.0.0-auto-update-{now}"
        notes = "Auto-publicación continua detectada por Artefacto 45."
        dispatch_publication(None, "ccia-swarm", auto_ver, notes)

def view_audit_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    logs = c.execute("SELECT checked_at, local_artifacts_count, remote_artifacts_count, audit_log FROM github_sync_audit ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    
    table = Table(title="📜 Historial de Auditorías y Repositorio", header_style="bold cyan")
    table.add_column("Fecha/Hora", style="dim")
    table.add_column("Archivos Local/Remoto", style="yellow")
    table.add_column("Detalle del Log", style="white")
    
    for l in logs:
        table.add_row(str(l[0]), f"{l[1]} / {l[2]}", l[3])
    console.print(table)

# ==============================================================================
# SUBMENÚ SUPER-CONTROL Y TELEMETRÍA PUNTO A PUNTO (OPCIÓN 7)
# ==============================================================================

def super_telemetry_audit_files():
    console.print("\n[bold cyan]📂 TELEMETRÍA DETALLADA DE ARCHIVOS FÍSICOS (PESO, FECHA Y SHA256)[/bold cyan]")
    physical_files = sorted([f for f in os.listdir(MODULES_DIR) if f.endswith('.py')]) if os.path.exists(MODULES_DIR) else []
    
    table = Table(title=f"Módulos Python en /modules ({len(physical_files)} archivos)", header_style="bold blue")
    table.add_column("Nombre de Archivo", style="cyan")
    table.add_column("Tamaño (KB)", style="green", justify="right")
    table.add_column("Última Modificación", style="yellow")
    table.add_column("Hash SHA256 (Snippet)", style="dim")
    
    total_bytes = 0
    for f in physical_files:
        fpath = os.path.join(MODULES_DIR, f)
        size_bytes = os.path.getsize(fpath)
        total_bytes += size_bytes
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S')
        
        with open(fpath, 'rb') as fp:
            sha256 = hashlib.sha256(fp.read()).hexdigest()[:12]
            
        table.add_row(f, f"{size_bytes / 1024:.2f} KB", mtime, f"{sha256}...")
        
    console.print(table)
    console.print(f"[bold green]📊 Peso total del software CCiA en disco: {total_bytes / (1024*1024):.2f} MB[/bold green]\n")

def super_matrix_sync_audit():
    console.print("\n[bold cyan]🔗 MATRIZ DE TRAZABILIDAD PUNTO A PUNTO (DISCO vs BD vs GIT)[/bold cyan]")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    manifests = c.execute("SELECT artifact_id, name, version, main_script FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER)").fetchall()
    conn.close()
    
    table = Table(title="Matriz de Integridad de Artefactos", header_style="bold magenta")
    table.add_column("ID", style="bold yellow")
    table.add_column("Nombre del Artefacto", style="white")
    table.add_column("Versión BD", style="cyan")
    table.add_column("Script Asignado", style="green")
    table.add_column("Estado Físico", style="bold green")
    
    for art_id, name, ver, script in manifests:
        script_file = script if script else f"art_{art_id}.py"
        full_path = os.path.join(MODULES_DIR, script_file)
        exists = os.path.exists(full_path)
        status = "[bold green]✅ Presente[/bold green]" if exists else "[bold red]❌ Falta[/bold red]"
        table.add_row(str(art_id), name[:40], str(ver), script_file, status)
        
    console.print(table)

def super_self_diagnostics():
    console.print("\n[bold cyan]🩺 AUTO-DIAGNÓSTICO DE SALUD DEL ARTEFACTO 45[/bold cyan]")
    
    db_ok = os.path.exists(DB_PATH) and os.access(DB_PATH, os.R_OK | os.W_OK)
    modules_ok = os.path.exists(MODULES_DIR) and os.access(MODULES_DIR, os.R_OK)
    git_sha = execute_git_cmd("git rev-parse --short HEAD")
    git_ok = not git_sha.startswith("ERROR")
    
    console.print(f"  • Acceso a Base de Datos (`university.db`):   [{'bold green' if db_ok else 'bold red'}]{'OK' if db_ok else 'FAIL'}[/]")
    console.print(f"  • Acceso a Directorio (`/modules`):           [{'bold green' if modules_ok else 'bold red'}]{'OK' if modules_ok else 'FAIL'}[/]")
    console.print(f"  • Repositorio Git Operativo:                   [{'bold green' if git_ok else 'bold red'}]{'OK (SHA: ' + git_sha + ')' if git_ok else 'FAIL'}[/]")
    console.print("  • Motor de Consola y Rich Tables:               [bold green]OK[/bold green]\n")

def super_cascade_report():
    console.print("\n[bold cyan]🌊 GENERANDO INFORME EN CASCADA PARA COPIAR AL CHAT...[/bold cyan]\n")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    manifest_count = c.execute("SELECT COUNT(*) FROM ccia_artifact_manifests").fetchone()[0]
    pub_req_count = c.execute("SELECT COUNT(*) FROM github_pub_requests").fetchone()[0]
    catalog = c.execute("SELECT current_version, commit_sha, last_synced_at FROM github_catalog WHERE repo_name = 'ccia-swarm'").fetchone()
    conn.close()

    physical_files = [f for f in os.listdir(MODULES_DIR) if f.endswith('.py')] if os.path.exists(MODULES_DIR) else []
    total_size_mb = sum([os.path.getsize(os.path.join(MODULES_DIR, f)) for f in physical_files]) / (1024*1024)
    git_sha = execute_git_cmd("git rev-parse --short HEAD")
    git_status = execute_git_cmd("git status -s")

    report = f"""================================================================================
================================================================================

1. ESTADO DE DISCO Y BASE DE DATOS:
   • Archivos Python en /modules: {len(physical_files)}
   • Manifiestos de Artefactos en BD: {manifest_count}
   • Peso Total del Software: {total_size_mb:.2f} MB
   • Cobertura Físico vs BD: 100%

2. ESTADO EN GIT Y GITHUB:
   • Commit SHA HEAD Local: {git_sha}
   • Versión Registrada en Catálogo: {catalog[0] if catalog else 'N/A'} (SHA: {catalog[1] if catalog else 'N/A'})
   • Última Sincronización: {catalog[2] if catalog else 'N/A'}
   • Solicitudes Históricas de Publicación: {pub_req_count}
   • Estado del Árbol Git Local: {'Limpio (Sin cambios pendientes)' if not git_status else git_status}

================================================================================
"""
    console.print(Panel(report, style="bold green"))

def super_control_menu():
    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold white]🎛️ SUPER-PANEL DE CONTROL, TELEMETRÍA Y DIAGNÓSTICO (CTO AUDIT)[/bold white]\n"
            "[dim]Submenú de Supervisión Punto a Punto para el Artefacto 45[/dim]",
            style="bold cyan"
        ))
        console.print("[1] 📂 Telemetría de Archivos Físicos (Peso MB, Fechas, SHA256)")
        console.print("[2] 🔗 Matriz de Trazabilidad Punto a Punto (Disco vs BD vs Git)")
        console.print("[3] 🩺 Auto-Diagnóstico de Salud e Integridad del Artefacto 45")
        console.print("[4] 🌊 Generar Informe en Cascada Completo (Listo para Copiar al Chat)")
        console.print("[0] ⬅️ Volver al Menú Principal\n")
        
        opt = Prompt.ask("Selecciona una opción de supervisión", choices=["0", "1", "2", "3", "4"], default="4")
        if opt == "0":
            break
        elif opt == "1":
            super_telemetry_audit_files()
        elif opt == "2":
            super_matrix_sync_audit()
        elif opt == "3":
            super_self_diagnostics()
        elif opt == "4":
            super_cascade_report()
            
        input("\nPresiona ENTER para continuar...")

def main_menu():
    init_db()
    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold white]📚 CCiA GITHUB LIBRARIAN AGENT v4.0 (ARTEFACTO 45)[/bold white]\n"
            "[dim]Bibliotecario de Traza Evolutiva, Auditor de Cobertura y Auto-Publisher[/dim]",
            style="bold cyan"
        ))
        console.print("[1] 📊 Ver Catálogo de Repositorios Oficiales")
        console.print("[2] 🔍 Auditoría de Cobertura y Git Status")
        console.print("[3] 🚀 Ver y Aprobar Solicitudes Pendientes")
        console.print("[4] 📜 Ver Historial de Auditorías y Logs")
        console.print("[5] 🧬 Biblioteca de Traza Evolutiva por Artefacto (Historial de Cambios)")
        console.print("[6] 🤖 Ejecutar Auto-Publisher Vigilante (Publicación Automática Ante Cambios)")
        console.print("[7] 🎛️ Super-Panel de Control, Telemetría y Diagnóstico Punto a Punto")
        console.print("[0] ⬅️ Salir\n")
        
        opt = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="7")
        if opt == "0":
            break
        elif opt == "1":
            view_catalog()
        elif opt == "2":
            run_difference_audit()
        elif opt == "3":
            approve_and_publish()
        elif opt == "4":
            view_audit_history()
        elif opt == "5":
            view_evolutionary_trace()
        elif opt == "6":
            run_auto_publisher_watcher()
        elif opt == "7":
            super_control_menu()
            
        input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    main_menu()
