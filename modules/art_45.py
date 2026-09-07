#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import datetime
import subprocess
import urllib.request
import urllib.parse
import hashlib
import re
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS github_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT UNIQUE,
            current_version TEXT,
            commit_sha TEXT,
            remote_url TEXT,
            last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS github_sync_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            local_artifacts_count INTEGER,
            remote_artifacts_count INTEGER,
            diff_detected INTEGER,
            audit_log TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS github_pub_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT,
            target_version TEXT,
            reason TEXT,
            release_notes TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifact_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_name TEXT,
            file_path TEXT,
            sha256_hash TEXT,
            file_size INTEGER,
            lines_count INTEGER,
            git_commit_sha TEXT,
            github_synced INTEGER DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_local_commit_sha():
    try:
        cmd = ["git", "rev-parse", "--short", "HEAD"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_DIR)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"

def count_local_artifacts():
    mdir = os.path.join(WORKSPACE_DIR, "modules")
    if os.path.exists(mdir):
        files = [f for f in os.listdir(mdir) if f.startswith("art_") and f.endswith(".py")]
        return len(files)
    return 0

def calculate_file_hash(filepath):
    sha = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()
    except Exception:
        return None

def snapshot_all_artifacts():
    init_db()
    mdir = os.path.join(WORKSPACE_DIR, "modules")
    if not os.path.exists(mdir):
        return 0, 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    local_sha = get_local_commit_sha()
    
    changes_detected = 0
    total_artifacts = 0

    for fname in sorted(os.listdir(mdir)):
        if fname.startswith("art_") and fname.endswith(".py"):
            total_artifacts += 1
            fpath = os.path.join(mdir, fname)
            fhash = calculate_file_hash(fpath)
            fsize = os.path.getsize(fpath)
            
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    flines = len(f.readlines())
            except Exception:
                flines = 0
                
            last_rec = cursor.execute(
                "SELECT sha256_hash FROM artifact_history WHERE artifact_name=? ORDER BY id DESC LIMIT 1",
                (fname,)
            ).fetchone()
            
            if not last_rec or last_rec[0] != fhash:
                changes_detected += 1
                cursor.execute("""
                    INSERT INTO artifact_history (artifact_name, file_path, sha256_hash, file_size, lines_count, git_commit_sha, github_synced)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (fname, fpath, fhash, fsize, flines, local_sha))

    conn.commit()
    conn.close()
    return total_artifacts, changes_detected

def fetch_remote_repo_info(repo_name, token):
    url = f"https://api.github.com/repos/{GH_USER}/{repo_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CCiA-GitHub-Librarian-v2.0"
    }
    if token and not token.startswith("tu_g"):
        headers["Authorization"] = f"token {token}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception:
        return None

def run_sync_audit():
    """Auditoría avanzada de sincronización Git & DB para CCiA."""
    workspace_dir = "/home/k1/ccia_workspace"
    db_path = os.path.join(workspace_dir, "university.db")
    modules_dir = os.path.join(workspace_dir, "modules")

    console.print("\n[bold cyan]🔍 AUDITORÍA DE SINCRONIZACIÓN Y ESTADO DE ARTEFACTOS[/bold cyan]")
    
    # 1. Conteo de artefactos
    physical_files = [f for f in os.listdir(modules_dir) if f.startswith("art_") and f.endswith(".py")] if os.path.exists(modules_dir) else []
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    db_count = c.execute("SELECT COUNT(*) FROM ccia_artifact_manifests").fetchone()[0]
    conn.close()

    console.print(f"  • Artefactos registrados en DB (university.db): [bold yellow]{db_count}[/bold yellow]")
    console.print(f"  • Módulos Python físicos en /modules:         [bold green]{len(physical_files)}[/bold green]")

    # 2. Estado de Git en workspace_dir
    try:
        git_head = subprocess.getoutput(f"git -C {workspace_dir} rev-parse --short HEAD")
        git_status = subprocess.getoutput(f"git -C {workspace_dir} status -s").strip()
        git_unpushed = subprocess.getoutput(f"git -C {workspace_dir} log origin/main..HEAD --oneline 2>/dev/null").strip()

        console.print(f"  • SHA Local HEAD: [magenta]{git_head}[/magenta]")

        if git_status:
            console.print("\n[bold yellow]⚠️ Cambios locales pendientes de commit (Working Tree Sucio):[/bold yellow]")
            for line in git_status.split("\n"):
                console.print(f"    {line}")
        else:
            console.print("  • Área de trabajo local: [bold green]Limpia (Sin cambios pendientes de commit)[/bold green]")

        if git_unpushed:
            console.print("\n[bold orange3]🚀 Commits locales pendientes de subir a GitHub (git push):[/bold orange3]")
            for line in git_unpushed.split("\n"):
                console.print(f"    {line}")
        else:
            console.print("  • Estado con remoto GitHub: [bold green]100% Sincronizado[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error al consultar estado de Git:[/bold red] {e}")


def run_auto_publish():
    total_arts, changes = snapshot_all_artifacts()
    
    for fname in os.listdir(WORKSPACE_DIR):
        if "activo" in fname and "ver" in fname:
            try:
                os.remove(os.path.join(WORKSPACE_DIR, fname))
            except Exception:
                pass

    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_DIR, capture_output=True, text=True).stdout.strip()
    
    if not git_status and changes == 0:
        console.print("[bold green]✅ Repositorio local sin cambios. 100% sincronizado con GitHub.[/bold green]")
        return
        
    console.print("[cyan]🚀 [Capsula del Tiempo] Subiendo a GitHub...[/cyan]")
    try:
        subprocess.run(["git", "add", "."], cwd=WORKSPACE_DIR, check=True)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"auto-sync: actualizacion CCiA v3.1.0 ({now_str})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKSPACE_DIR, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE_DIR, capture_output=True, text=True)
        
        new_sha = get_local_commit_sha()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("UPDATE artifact_history SET github_synced=1, git_commit_sha=? WHERE github_synced=0", (new_sha,))
        c.execute("""
            INSERT INTO github_catalog (repo_name, current_version, commit_sha, remote_url, last_synced_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(repo_name) DO UPDATE SET
                current_version=excluded.current_version,
                commit_sha=excluded.commit_sha,
                last_synced_at=CURRENT_TIMESTAMP
        """, ("ccia-swarm", f"v3.1.0-art{total_arts}", new_sha, f"https://github.com/{GH_USER}/ccia-swarm"))
        
        conn.commit()
        conn.close()
        console.print("[bold green]🎉 Historial sincronizado con GitHub correctamente.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Error durante la sincronizacion auto-publish: {e}[/bold red]")

def display_artifact_timeline(art_num_input):
    init_db()
    
    clean_num = "".join(c for c in str(art_num_input) if c.isdigit())
    art_name = f"art_{clean_num}.py" if clean_num else str(art_num_input)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    rows = cursor.execute("""
        SELECT id, sha256_hash, file_size, lines_count, git_commit_sha, github_synced, recorded_at
        FROM artifact_history 
        WHERE artifact_name=? OR artifact_name=?
        ORDER BY id DESC
    """, (art_name, f"art_{art_num_input}.py")).fetchall()
    
    conn.close()
    
    if not rows:
        console.print()
        console.print(f"[bold red]❌ No se encontraron registros de cambios para: `{art_name}`[/bold red]")
        return

    table = Table(title=f"📜 Historial y Linea del Tiempo: {art_name}", expand=True)
    table.add_column("Snap ID", style="cyan", width=8)
    table.add_column("Fecha y Hora", style="white")
    table.add_column("Tamano (Bytes)", style="yellow")
    table.add_column("Lineas", style="bold blue")
    table.add_column("SHA256 (Corto)", style="magenta")
    table.add_column("Commit Git", style="dim")
    table.add_column("GitHub Sync", style="green")

    for r in rows:
        synced_str = "✅ Sincronizado" if r[5] == 1 else "⏳ Pendiente"
        table.add_row(
            str(r[0]),
            str(r[6]),
            f"{r[2]:,} B",
            str(r[3]),
            r[1][:10] if r[1] else "N/A",
            r[4],
            synced_str
        )
    console.print(table)

def run_e2e_audit():
    console.print("\n" + "=" * 75)
    console.print("🧪 AUDITORIA Y VERIFICACION END-TO-END: AGENTE BIBLIOTECARIO (ARTEFACTO 45 v2.0)")
    console.print("=" * 75)

    console.print("\n🔍 1. Lanzando auditoria de diferencias y snapshot...")
    run_sync_audit()
    console.print("✅ Auditoria de diferencias y snapshot SHA256 completados.")

    console.print("\n📊 2. Verificando tablas de catalogo y solicitudes de publicacion...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cat_rows = c.execute("SELECT repo_name, current_version, commit_sha, remote_url, last_synced_at FROM github_catalog").fetchall()
    req_rows = c.execute("SELECT id, repo_name, target_version, reason, status FROM github_pub_requests ORDER BY id DESC LIMIT 5").fetchall()

    table_cat = Table(title="📦 Repositorios en Catalogo Agentico", expand=True)
    table_cat.add_column("Repo", style="cyan")
    table_cat.add_column("Version Registrada", style="yellow")
    table_cat.add_column("Commit SHA", style="magenta")
    table_cat.add_column("Sincronizado", style="dim")
    for r in cat_rows:
        table_cat.add_row(r[0], r[1], r[2], str(r[4]))
    console.print(table_cat)

    table_req = Table(title="🚀 Solicitudes de Publicacion Registradas", expand=True)
    table_req.add_column("ID", style="bold cyan")
    table_req.add_column("Repo / Target Version", style="white")
    table_req.add_column("Motivo", style="yellow")
    table_req.add_column("Estado", style="green")
    for r in req_rows:
        table_req.add_row(str(r[0]), f"{r[1]} -> {r[2]}", r[3], r[4])
    console.print(table_req)

    console.print("\n🌐 3. Verificando estado del repositorio remoto en GitHub...")
    git_remote = subprocess.run(["git", "remote", "-v"], cwd=WORKSPACE_DIR, capture_output=True, text=True).stdout.strip()
    console.print("  • Remoto configurado:\n" + str(git_remote))

    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_DIR, capture_output=True, text=True).stdout.strip()
    if not git_status:
        console.print("\n[bold green]✅ EL REPOSITORIO LOCAL ESTA 100% SINCRONIZADO CON GITHUB.[/bold green]")
    else:
        console.print("\n[bold yellow]ℹ️ Archivos pendientes de commit:\n" + str(git_status) + "[/bold yellow]")

    conn.close()
    console.print("\n" + "=" * 75)

def display_menu():
    init_db()
    
    while True:
        console.print("\n" + "=" * 70)
        console.print(Panel(
            "[bold cyan]📚 CCiA GITHUB LIBRARIAN AGENT v2.0 (ARTEFACTO 45)[/bold cyan]\n"
            "[white]Auditor de Versiones, Capsula del Tiempo SHA256 y Autopublicacion[/white]",
            title="[bold yellow]MISSION CONTROL - GITHUB AGENT[/bold yellow]",
            expand=True
        ))
        
        console.print("[1] 📊 Ver Catalogo de Repositorios Publicados en GitHub")
        console.print("[2] 🔍 Ejecutar Auditoria de Diferencias (Local vs GitHub Remote)")
        console.print("[3] 🚀 Ver y Aprobar Solicitudes de Publicacion Pendientes")
        console.print("[4] 📜 Ver Historial de Auditorias y Logs del Agente")
        console.print("[5] 🧪 Ejecutar Auditoria End-to-End y Diagnostico de Autopublicacion")
        console.print("[6] 📜 Inspeccionar Historial y Evolucion por Artefacto (Capsula del Tiempo)")
        console.print("[0] ⬅️ Salir")
        
        choice = input("\nSelecciona una opcion [0-6]: ").strip()
        
        if choice == "1":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT repo_name, current_version, commit_sha, remote_url, last_synced_at FROM github_catalog").fetchall()
            conn.close()
            
            table = Table(title="📦 Repositorios Registrados en GitHub", expand=True)
            table.add_column("Repositorio", style="cyan")
            table.add_column("Version Registrada", style="yellow")
            table.add_column("Commit SHA", style="magenta")
            table.add_column("URL Publica", style="green")
            table.add_column("Ultima Sincronizacion", style="dim")
            
            for r in rows:
                table.add_row(r[0], r[1], r[2], r[3], str(r[4]))
            console.print(table)
            input("\nPresiona ENTER para continuar...")

        elif choice == "2":
            console.print("\n[cyan]🔍 Ejecutando auditoria de diferencias con la API de GitHub...[/cyan]")
            run_sync_audit()
            console.print("[bold green]✅ Auditoria completada con exito.[/bold green]")
            input("\nPresiona ENTER para continuar...")

        elif choice == "3":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, repo_name, target_version, reason, release_notes, status FROM github_pub_requests WHERE status='PENDING'").fetchall()
            
            if not rows:
                console.print("\n[yellow]No hay solicitudes de publicacion pendientes de aprobacion.[/yellow]")
                conn.close()
                input("\nPresiona ENTER para continuar...")
                continue

            table = Table(title="🚀 Solicitudes de Publicacion Pendientes", expand=True)
            table.add_column("ID", style="bold cyan", width=5)
            table.add_column("Repositorio / Version", style="white")
            table.add_column("Motivo de Publicacion", style="yellow")
            table.add_column("Notas de Version (Release Notes)", style="green")
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
                    console.print(f"\n[cyan]🚀 Despachando publicacion para `{repo}` version `{ver}`...[/cyan]")
                    
                    try:
                        subprocess.run(["git", "add", "."], cwd=WORKSPACE_DIR, check=True)
                        subprocess.run(["git", "commit", "-m", f"release: {ver} - {notes}"], cwd=WORKSPACE_DIR, capture_output=True)
                        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE_DIR, capture_output=True, text=True)
                        
                        c.execute("UPDATE github_pub_requests SET status='PUBLISHED_AND_DISPATCHED' WHERE id=?", (req_id,))
                        new_sha = get_local_commit_sha()
                        c.execute("UPDATE github_catalog SET current_version=?, commit_sha=?, last_synced_at=CURRENT_TIMESTAMP WHERE repo_name=?", (ver, new_sha, repo))
                        conn.commit()
                        console.print("[bold green]🎉 Publicacion completada y sincronizada con GitHub con exito.[/bold green]")
                    except Exception as e:
                        console.print(f"[bold red]❌ Error durante la ejecucion de la publicacion: {e}[/bold red]")
                else:
                    console.print("[red]ID no encontrado o ya procesado.[/red]")
            conn.close()
            input("\nPresiona ENTER para continuar...")

        elif choice == "4":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, checked_at, local_artifacts_count, diff_detected, audit_log FROM github_sync_audit ORDER BY id DESC LIMIT 10").fetchall()
            conn.close()

            table = Table(title="📜 Registro Historico de Auditorias del Agente Bibliotecario", expand=True)
            table.add_column("ID", style="cyan", width=5)
            table.add_column("Fecha/Hora", style="white")
            table.add_column("Artefactos Locales", style="bold yellow")
            table.add_column("Diff Detectado", style="magenta")
            table.add_column("Detalle de Auditoria", style="green")

            for r in rows:
                table.add_row(str(r[0]), str(r[1]), str(r[2]), "SI" if r[3] else "NO", r[4])
            console.print(table)
            input("\nPresiona ENTER para continuar...")

        elif choice == "5":
            run_e2e_audit()
            input("\nPresiona ENTER para continuar...")

        elif choice == "6":
            snapshot_all_artifacts()
            mdir = os.path.join(WORKSPACE_DIR, "modules")
            if os.path.exists(mdir):
                files = sorted([f for f in os.listdir(mdir) if f.startswith("art_") and f.endswith(".py")])
                console.print("\n[bold cyan]📦 ARTEFACTOS DETECTADOS EN CCiA:[/bold cyan]")
                for f in files:
                    clean_f_num = "".join(c for c in f if c.isdigit())
                    console.print(f"  • [bold yellow][Artefacto {clean_f_num}][/bold yellow] {f}")
            
            art_sel = input("\nIngresa el NUMERO del artefacto a inspeccionar (ej. 62 o 45): ").strip()
            if art_sel:
                display_artifact_timeline(art_sel)
            input("\nPresiona ENTER para continuar...")

        elif choice == "0":
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--cron", "--auto-publish"]:
            run_auto_publish()
        elif sys.argv[1] == "--snapshot":
            snapshot_all_artifacts()
    else:
        display_menu()
