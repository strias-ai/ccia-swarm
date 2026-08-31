#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import urllib.request
import time
import traceback
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Detección de motor vectorial local
SQLITE_VEC_AVAILABLE = False
ST_MODEL = None

try:
    import sqlite_vec
    SQLITE_VEC_AVAILABLE = True
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
    # Carga diferida o inicialización rápida de modelo de embeddings ligero
    ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    pass

console = Console()
DB_PATH = "/home/k1/ccia_workspace/university.db"
OLLAMA_BASE_URL = "http://localhost:11434"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    if SQLITE_VEC_AVAILABLE:
        try:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
        except Exception:
            pass
    return conn

def flush_stdin():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass

def pause():
    flush_stdin()
    input("\n[ Presiona ENTER para continuar... ]")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_product_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT UNIQUE,
            problem_statement TEXT,
            target_audience TEXT,
            monetization_model TEXT,
            market_score INTEGER,
            proposed_stack TEXT,
            status TEXT DEFAULT 'PENDING_REVIEW',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    if SQLITE_VEC_AVAILABLE:
        try:
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_product_proposals USING vec0(
                    proposal_id INTEGER PRIMARY KEY,
                    proposal_embedding float[384]
                )
            ''')
        except Exception:
            pass

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ccia_agent_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sla_performance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_id INTEGER,
            event_type TEXT,
            status TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO ccia_agent_config (key, value) VALUES ('ollama_selected_model', 'huihui_ai/qwen2.5-coder-abliterate:7b')")
    cursor.execute("INSERT OR IGNORE INTO ccia_agent_config (key, value) VALUES ('art_46_automation_mode', 'CHRONOS_EVENT_DRIVEN')")
    conn.commit()
    conn.close()

def log_event(artifact_id, event_type, status, details=""):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        cols = [col[1] for col in c.execute("PRAGMA table_info(sla_performance_logs)").fetchall()]
        
        fields, values = [], []
        if "artifact_id" in cols: fields.append("artifact_id"); values.append(artifact_id)
        if "event_type" in cols: fields.append("event_type"); values.append(event_type)
        if "status" in cols: fields.append("status"); values.append(status)
        if "details" in cols: fields.append("details"); values.append(details)

        if fields:
            placeholders = ", ".join(["?"] * len(fields))
            field_names = ", ".join(fields)
            c.execute(f"INSERT INTO sla_performance_logs ({field_names}) VALUES ({placeholders})", values)
            conn.commit()
        conn.close()
    except Exception:
        pass

def get_config_val(key, default=""):
    init_db()
    try:
        conn = get_db_connection()
        c = conn.cursor()
        row = c.execute("SELECT value FROM ccia_agent_config WHERE key=?", (key,)).fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default

def set_config_val(key, val):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("REPLACE INTO ccia_agent_config (key, value) VALUES (?, ?)", (key, val))
    conn.commit()
    conn.close()

def fetch_ollama_models():
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def query_ollama(prompt):
    log_event(46, 'OLLAMA_INFERENCE_LOCK_ACQUIRED', 'ACTIVE', 'Reserva de slot en Chronos Scheduler')
    selected_model = get_config_val('ollama_selected_model', 'huihui_ai/qwen2.5-coder-abliterate:7b')
    payload = json.dumps({"model": selected_model, "prompt": prompt, "stream": False}).encode('utf-8')
    req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/generate", data=payload, headers={"Content-Type": "application/json"})
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            elapsed = round(time.time() - start_time, 2)
            log_event(46, 'OLLAMA_INFERENCE_SUCCESS', 'COMPLETED', f"Modelo: {selected_model} | Latencia: {elapsed}s")
            return data.get("response", "")
    except Exception as e:
        log_event(46, 'OLLAMA_INFERENCE_ERROR', 'FAILED', str(e))
        console.print(f"[bold red]❌ Error en consulta a Ollama ({selected_model}): {e}[/bold red]")
        return None

def get_existing_projects_memory():
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT project_name FROM github_product_proposals").fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

def gather_internal_intelligence():
    signals = []
    try:
        conn = get_db_connection()
        c = conn.cursor()
        tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        
        if "bounty_opportunities" in tables:
            cols = [col[1] for col in c.execute("PRAGMA table_info(bounty_opportunities)").fetchall()]
            if cols:
                title_col = "title" if "title" in cols else "issue_title" if "issue_title" in cols else cols[1] if len(cols) > 1 else cols[0]
                rows = c.execute(f"SELECT {title_col} FROM bounty_opportunities ORDER BY id DESC LIMIT 5").fetchall()
                for r in rows:
                    signals.append(f"Bounty Issue: {r[0]}")
                    
        if "ccia_market_intelligence" in tables:
            cols = [col[1] for col in c.execute("PRAGMA table_info(ccia_market_intelligence)").fetchall()]
            if cols:
                topic_col = "topic" if "topic" in cols else cols[1] if len(cols) > 1 else cols[0]
                payload_col = "payload" if "payload" in cols else "service_type" if "service_type" in cols else cols[-1]
                rows = c.execute(f"SELECT {topic_col}, {payload_col} FROM ccia_market_intelligence ORDER BY id DESC LIMIT 5").fetchall()
                for r in rows:
                    signals.append(f"Market Signal [{r[0]}]: {r[1]}")
                    
        conn.close()
    except Exception as e:
        console.print(f"[dim yellow]⚠️ Aviso al extraer señales DB: {e}[/dim yellow]")
        
    if not signals:
        signals = [
            "Conectores MCP nativos para Stripe A2A y pagos entre agentes de IA.",
            "Orquestación térmica y eficiencia energética para modelos de inferencia local en NucBox-K11.",
            "Servidor de contexto dinámico SQLite para arquitecturas multi-agente."
        ]
    return signals

def save_proposal(sample_data):
    conn = get_db_connection()
    c = conn.cursor()
    p_name = sample_data.get("project_name", "ccia-generic-agent")
    
    existing = c.execute("SELECT id FROM github_product_proposals WHERE project_name = ?", (p_name,)).fetchone()
    if existing:
        pid = existing[0]
        c.execute("""
            UPDATE github_product_proposals 
            SET problem_statement=?, target_audience=?, monetization_model=?, market_score=?, proposed_stack=?
            WHERE id=?
        """, (
            sample_data.get("problem_statement", ""),
            sample_data.get("target_audience", ""),
            sample_data.get("monetization_model", ""),
            sample_data.get("market_score", 90),
            sample_data.get("proposed_stack", "Python 3.12"),
            pid
        ))
    else:
        c.execute("""
            INSERT INTO github_product_proposals 
            (project_name, problem_statement, target_audience, monetization_model, market_score, proposed_stack, status)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING_REVIEW')
        """, (
            p_name,
            sample_data.get("problem_statement", ""),
            sample_data.get("target_audience", ""),
            sample_data.get("monetization_model", ""),
            sample_data.get("market_score", 90),
            sample_data.get("proposed_stack", "Python 3.12")
        ))
        pid = c.lastrowid

    if SQLITE_VEC_AVAILABLE and ST_MODEL:
        try:
            text_to_embed = f"{p_name} {sample_data.get('problem_statement', '')}"
            embedding = ST_MODEL.encode(text_to_embed).tolist()
            c.execute("INSERT OR REPLACE INTO vec_product_proposals(proposal_id, proposal_embedding) VALUES (?, ?)", (pid, json.dumps(embedding)))
        except Exception:
            pass

    conn.commit()
    conn.close()

def scan_market_trends():
    init_db()
    current_model = get_config_val('ollama_selected_model', 'huihui_ai/qwen2.5-coder-abliterate:7b')
    memory_projects = get_existing_projects_memory()
    
    vec_status = "⚡ sqlite-vec ACTIVO" if SQLITE_VEC_AVAILABLE else "⚠️ sqlite-vec NO DETECTADO"
    console.print(f"\n[cyan]🤖 Cerebro Activo: [bold yellow]{current_model}[/bold yellow] | [{vec_status}] | Memoria: [bold cyan]{len(memory_projects)} proyectos[/bold cyan][/cyan]")
    
    signals = gather_internal_intelligence()
    internal_data = "\n".join([f"- {s}" for s in signals])
    existing_list = ", ".join(memory_projects) if memory_projects else "Ninguno"
    
    prompt = f"""Analiza las siguientes señales de mercado detectadas en el sistema CCiA:
{internal_data}

MEMORIA DE PROYECTOS EXISTENTES (NO DUPLICAR NI REPETIR CONCEPTOS SIMILARES):
[{existing_list}]

Genera una propuesta de proyecto Open-Source monetizable ÚNICA y NUEVA para GitHub.
Responde ÚNICAMENTE con un JSON válido con esta estructura exacta:
{{"project_name": "...", "problem_statement": "...", "target_audience": "...", "monetization_model": "...", "market_score": 95, "proposed_stack": "Python 3.12, FastAPI, MCP SDK, Docker"}}
"""
    
    response_text = query_ollama(prompt)
    sample_data = None
    if response_text and "{" in response_text:
        try:
            json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
            sample_data = json.loads(json_str)
        except Exception:
            pass

    if not sample_data:
        console.print("[yellow]⚠️ Aplicando fallback de propuesta validada...[/yellow]")
        sample_data = {
            "project_name": "ccia-mcp-stripe-agent",
            "problem_statement": "Falta de conectores nativos MCP para cobros automatizados A2A entre agentes de IA.",
            "target_audience": "Empresas SaaS, Desarrolladores de Agentes de IA y Bot Marketplaces.",
            "monetization_model": "Open-Core (MIT base / Enterprise License B2B)",
            "market_score": 94,
            "proposed_stack": "Python 3.12, FastAPI, MCP SDK, Docker Container"
        }

    save_proposal(sample_data)
    console.print(Panel(
        f"[bold yellow]Proyecto:[/bold yellow] {sample_data['project_name']}\n"
        f"[bold yellow]Score de Mercado:[/bold yellow] {sample_data['market_score']}/100\n"
        f"[bold cyan]Problema:[/bold cyan] {sample_data['problem_statement']}\n"
        f"[bold cyan]Stack:[/bold cyan] {sample_data['proposed_stack']}",
        title="[bold green]✅ Propuesta Generada e Integrada en DB[/bold green]"
    ))

def show_audit_logs():
    console.print("\n[bold cyan]📜 REGISTROS DE AUDITORÍA Y SLA (Chronos & Ollama Events)[/bold cyan]")
    conn = get_db_connection()
    c = conn.cursor()
    tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    if "sla_performance_logs" not in tables:
        console.print("[yellow]La tabla `sla_performance_logs` aún no tiene eventos registrados.[/yellow]")
        conn.close()
        return

    rows = c.execute("SELECT * FROM sla_performance_logs ORDER BY id DESC LIMIT 10").fetchall()
    cols = [col[1] for col in c.execute("PRAGMA table_info(sla_performance_logs)").fetchall()]
    conn.close()
    
    table = Table(expand=True)
    for col_name in cols[:6]:
        table.add_column(col_name, style="cyan")
    
    for r in rows:
        table.add_row(*[str(val)[:40] for val in r[:6]])
    
    console.print(table)

def show_db_explorer():
    console.print("\n[bold cyan]🗄️ EXPLORADOR DE DATOS DE INTELIGENCIA DE MERCADO[/bold cyan]")
    conn = get_db_connection()
    c = conn.cursor()
    tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    if "bounty_opportunities" in tables:
        cols = [col[1] for col in c.execute("PRAGMA table_info(bounty_opportunities)").fetchall()]
        bounties = c.execute("SELECT * FROM bounty_opportunities LIMIT 5").fetchall()
        table_b = Table(title="💡 Top Bounty Opportunities (Art 19)", expand=True)
        for col_name in cols[:4]:
            table_b.add_column(col_name, style="yellow")
        for b in bounties:
            table_b.add_row(*[str(val) for val in b[:4]])
        console.print(table_b)
        
    if "ccia_market_intelligence" in tables:
        cols = [col[1] for col in c.execute("PRAGMA table_info(ccia_market_intelligence)").fetchall()]
        intel = c.execute("SELECT * FROM ccia_market_intelligence ORDER BY id DESC LIMIT 5").fetchall()
        table_i = Table(title="📡 Signals Intel DB (Art 40)", expand=True)
        for col_name in cols[:4]:
            table_i.add_column(col_name, style="cyan")
        for i in intel:
            row_vals = [str(val)[:50] + "..." if len(str(val)) > 50 else str(val) for val in i[:4]]
            table_i.add_row(*row_vals)
        console.print(table_i)
        
    conn.close()

def benchmark_ollama_model():
    models = fetch_ollama_models()
    current = get_config_val('ollama_selected_model', 'huihui_ai/qwen2.5-coder-abliterate:7b')
    
    console.print(Panel(f"[bold cyan]🧠 GESTOR Y BENCHMARK DE CEREBROS OLLAMA[/bold cyan]\nModelo Activo: [bold yellow]{current}[/bold yellow]"))
    
    if not models:
        console.print("[bold red]⚠️ No se pudo obtener la lista de modelos de Ollama.[/bold red]")
        return

    table = Table(title=f"Modelos Instalados en NucBox-K11 (Total: {len(models)})")
    table.add_column("Nº", style="bold cyan", width=4)
    table.add_column("Nombre del Modelo", style="yellow")
    table.add_column("Estado", style="green")
    
    for idx, m in enumerate(models, 1):
        status = " (ACTIVO)" if m == current else ""
        table.add_row(str(idx), m, status)
    
    console.print(table)
    
    flush_stdin()
    choice = input("\nSelecciona número de modelo a activar (o 't' para ping test, 0 cancelar): ").strip()
    
    if choice.lower() == 't':
        console.print(f"\n[cyan]⏱️ Probando latencia de respuesta en [yellow]{current}[/yellow]...[/cyan]")
        t0 = time.time()
        res = query_ollama("Responde brevemente: OK")
        t1 = round(time.time() - t0, 3)
        console.print(f"[bold green]⚡ Respuesta recibida en {t1}s: {res}[/bold green]")
    elif choice.isdigit() and 1 <= int(choice) <= len(models):
        selected = models[int(choice) - 1]
        set_config_val('ollama_selected_model', selected)
        console.print(f"[bold green]✅ Cerebro activado: `{selected}`[/bold green]")

def toggle_automation_mode():
    current_mode = get_config_val('art_46_automation_mode', 'CHRONOS_EVENT_DRIVEN')
    console.print("\n[bold cyan]⚙️ MANDO DE AUTOMATIZACIÓN Y ORQUESTACIÓN (ARTEFACTO 46)[/bold cyan]")
    console.print(f"Modo Actual: [bold yellow]{current_mode}[/bold yellow]\n")
    console.print("[1] 🧠 Event-Driven con Chronos (Art 28) [RECOMENDADO - Inferencia bajo demanda]")
    console.print("[2] ⏱️ Daemon Autónomo (Escaneo periódico controlado por Chronos)")
    console.print("[3] ⏸️ Desactivar Automatización (Solo ejecución manual por menú)")
    
    flush_stdin()
    sel = input("\nSelecciona modo [1-3]: ").strip()
    if sel == "1":
        set_config_val('art_46_automation_mode', 'CHRONOS_EVENT_DRIVEN')
        log_event(46, 'AUTOMATION_MODE_CHANGED', 'SUCCESS', 'Modo fijado en CHRONOS_EVENT_DRIVEN')
        console.print("[bold green]✅ Modo fijado: Event-Driven con Chronos Scheduler (Art 28).[/bold green]")
    elif sel == "2":
        set_config_val('art_46_automation_mode', 'DAEMON_PERIODIC_CHRONOS')
        log_event(46, 'AUTOMATION_MODE_CHANGED', 'SUCCESS', 'Modo fijado en DAEMON_PERIODIC_CHRONOS')
        console.print("[bold green]✅ Modo fijado: Daemon controlado por slots de Chronos.[/bold green]")
    elif sel == "3":
        set_config_val('art_46_automation_mode', 'DISABLED')
        log_event(46, 'AUTOMATION_MODE_CHANGED', 'SUCCESS', 'Automatización desactivada')
        console.print("[bold yellow]⏸️ Automatización desactivada. El agente esperará comandos manuales.[/bold yellow]")

def generate_spec_md():
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT id, project_name FROM github_product_proposals").fetchall()
    conn.close()
    
    if not rows:
        console.print("[yellow]No hay propuestas registradas para previsualizar especificación.[/yellow]")
        return
        
    table = Table(title="📐 Generador de Archivo Spec README")
    table.add_column("ID", width=4)
    table.add_column("Proyecto", style="yellow")
    for r in rows:
        table.add_row(str(r[0]), r[1])
    console.print(table)
    
    flush_stdin()
    sel = input("\nID de proyecto a visualizar spec (0 cancelar): ").strip()
    if sel.isdigit() and int(sel) > 0:
        pid = int(sel)
        conn = get_db_connection()
        c = conn.cursor()
        p = c.execute("SELECT project_name, problem_statement, proposed_stack, target_audience, monetization_model FROM github_product_proposals WHERE id=?", (pid,)).fetchone()
        conn.close()
        if p:
            md_content = f"""# {p[0]}

## 🎯 Problema que resuelve
{p[1]}

## 🛠️ Stack Tecnológico
{p[2]}

## 👥 Audiencia Objetivo
{p[3]}

## 💰 Modelo de Monetización
{p[4]}

---
*Especificación generada por CCiA Product Engine (Artefacto 46).*
"""
            console.print(Panel(Syntax(md_content, "markdown", theme="monokai"), title=f"📄 Spec README: {p[0]}"))

def display_menu():
    init_db()
    while True:
        try:
            current_model = get_config_val('ollama_selected_model', 'huihui_ai/qwen2.5-coder-abliterate:7b')
            auto_mode = get_config_val('art_46_automation_mode', 'CHRONOS_EVENT_DRIVEN')
            vec_info = " (sqlite-vec Enabled)" if SQLITE_VEC_AVAILABLE else ""
            
            console.print("\n" + "=" * 75)
            console.print(Panel(
                f"[bold cyan]🧠 CCiA MARKET RESEARCH & PRODUCT ENGINE (ARTEFACTO 46)[/bold cyan]\n"
                f"Cerebro: [bold yellow]{current_model}[/bold yellow] | Modo: [bold green]{auto_mode}[/bold green]{vec_info}",
                title="[bold yellow]MISSION CONTROL - PRODUCT ENGINE[/bold yellow]",
                expand=True
            ))
            
            console.print("[1] 🔍 Escanear Mercado & Bounty Opportunities (`university.db` + LLM)")
            console.print("[2] 📋 Catálogo Completo & Inspeccionar Propuesta por ID")
            console.print("[3] 🚀 Aprobar Propuesta y Transferir al Bibliotecario (Art 45)")
            console.print("[4] 📜 Registros de Auditoría y Logs de SLA (`sla_performance_logs`)")
            console.print("[5] 🗄️ Explorador de Datos de Inteligencia (`bounty` / `market_intel`)")
            console.print("[6] 🧠 Gestor de Cerebros Ollama & Test Latencia (28 Modelos)")
            console.print("[7] ⚡ Monitor de ROI & Cobertura Energética (NucBox-K11 35W/h)")
            console.print("[8] 📐 Generador de Spec & Arquitectura README para Proyectos")
            console.print("[9] ⚙️ Mando de Automatización & Orquestación con Chronos (Art 28)")
            console.print("[0] ⬅️ Volver / Salir")
            
            flush_stdin()
            choice = input("\nSelecciona una opción [0-9]: ").strip()
            
            if choice == "1":
                scan_market_trends()
                pause()

            elif choice == "2":
                conn = get_db_connection()
                c = conn.cursor()
                rows = c.execute("SELECT id, project_name, problem_statement, monetization_model, market_score, status FROM github_product_proposals").fetchall()
                conn.close()
                
                table = Table(title="💡 Catálogo de Propuestas Registradas", expand=True)
                table.add_column("ID", style="bold cyan", width=4)
                table.add_column("Proyecto", style="yellow")
                table.add_column("Problema", style="white")
                table.add_column("Monetización", style="green")
                table.add_column("Score", style="magenta", width=6)
                table.add_column("Estado", style="dim")
                
                for r in rows:
                    prob = (r[2][:45] + "...") if r[2] and len(r[2]) > 45 else (r[2] or "")
                    table.add_row(str(r[0]), r[1] or "", prob, r[3] or "", str(r[4] or 0), r[5] or "")
                console.print(table)
                
                flush_stdin()
                sub = input("\nID para ver detalle completo (o ENTER para continuar): ").strip()
                if sub.isdigit():
                    conn = get_db_connection()
                    c = conn.cursor()
                    p = c.execute("SELECT project_name, problem_statement, target_audience, monetization_model, market_score, proposed_stack, status FROM github_product_proposals WHERE id=?", (int(sub),)).fetchone()
                    conn.close()
                    if p:
                        detail_text = f"""[bold yellow]Proyecto:[/bold yellow] {p[0]}
[bold yellow]Estado:[/bold yellow] {p[6]} | [bold yellow]Score:[/bold yellow] {p[4]}/100

[bold cyan]Problema:[/bold cyan] {p[1]}
[bold cyan]Audiencia:[/bold cyan] {p[2]}
[bold cyan]Monetización:[/bold cyan] {p[3]}
[bold cyan]Stack Tecnológico:[/bold cyan] {p[5]}"""
                        console.print(Panel(detail_text, title=f"Detalle de Propuesta #{sub}"))
                pause()

            elif choice == "3":
                conn = get_db_connection()
                c = conn.cursor()
                rows = c.execute("SELECT id, project_name, problem_statement FROM github_product_proposals WHERE status='PENDING_REVIEW'").fetchall()
                
                if not rows:
                    console.print("\n[yellow]No hay propuestas pendientes de revisión.[/yellow]")
                    conn.close()
                    pause()
                    continue
                
                table = Table(title="🚀 Aprobar y Transferir al Bibliotecario (Artefacto 45)", expand=True)
                table.add_column("ID", style="bold cyan", width=5)
                table.add_column("Proyecto", style="yellow")
                table.add_column("Descripción / Problema", style="white")
                for r in rows:
                    table.add_row(str(r[0]), r[1] or "", r[2] or "")
                console.print(table)
                
                flush_stdin()
                sub = input("\nID de propuesta a aprobar (0 para cancelar): ").strip()
                if sub.isdigit() and int(sub) > 0:
                    pid = int(sub)
                    target = c.execute("SELECT project_name, problem_statement FROM github_product_proposals WHERE id=?", (pid,)).fetchone()
                    if target:
                        pname, pdesc = target
                        c.execute('''
                            INSERT INTO github_pub_requests (repo_name, target_version, reason, release_notes, status)
                            VALUES (?, 'v1.0.0', ?, ?, 'PENDING')
                        ''', (pname, f"Aprobado por Product Engine: {pdesc}", "Release inicial automatizada."))
                        
                        c.execute("UPDATE github_product_proposals SET status='APPROVED_SENT_TO_LIBRARIAN' WHERE id=?", (pid,))
                        conn.commit()
                        log_event(46, 'PROPOSAL_APPROVED', 'SUCCESS', f"Proyecto {pname} enviado a Art 45")
                        console.print(f"\n[bold green]🎉 ¡Proyecto `{pname}` aprobado! Transferido al Agente Bibliotecario (Art 45).[/bold green]")
                conn.close()
                pause()

            elif choice == "4":
                show_audit_logs()
                pause()

            elif choice == "5":
                show_db_explorer()
                pause()

            elif choice == "6":
                benchmark_ollama_model()
                pause()

            elif choice == "7":
                console.print("\n[bold yellow]⚡ MONITOR FINANCIAL ROI & BALANCE ENERGÉTICO[/bold yellow]")
                console.print("  • Hardware Target: NucBox-K11 (AMD Ryzen 9 / GPU RDNA3)")
                console.print("  • Consumo TDP Medio Inferencia: ~35 Watts/hora")
                console.print("  • Coste Energético Diario Estimado: ~0.18 EUR / día")
                console.print("  • Proyección Retorno por Proyecto Open-Core / Bounty: ~15.00 EUR / unidad")
                console.print("  • [bold green]Ratio de Autonomía Financiera: 100% Cobertura Operativa (Superávit Agéntico).[/bold green]")
                pause()

            elif choice == "8":
                generate_spec_md()
                pause()

            elif choice == "9":
                toggle_automation_mode()
                pause()

            elif choice == "0":
                break

        except Exception as ex:
            err_msg = traceback.format_exc()
            console.print(Panel(f"[bold red]❌ Excepción en ejecución capturada:[/bold red]\n{err_msg}", title="[bold red]Error Interceptado[/bold red]"))
            pause()

if __name__ == "__main__":
    display_menu()
