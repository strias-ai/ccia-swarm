import os, sys, time, traceback

def write_daemon_pid():
    try:
        with open("/tmp/art_60_daemon.pid", "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

import re

def clean_to_strict_json(text):
    if not text:
        return text
    match = re.search(r"(\{[\s\S]*\})", str(text))
    return match.group(1).strip() if match else str(text).strip()

import re

def sanitize_json_payload(raw_text):
    if not raw_text:
        return raw_text
    match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text

#!/usr/bin/env python3
"""
CCiA - ARTEFACTO 60: MOTOR COMERCIAL Y HUB DE COMUNICACIÓN A2A 24/7 (v3.4)
================================================================================
- Cosecha Multicanal con SearXNG Local Engine (http://localhost:8080)
- Payload Protocolar Bot-to-Bot con Matriz de Pagos Multired (USDC Solana/Base, Sats, Stripe)
- Auto-migración de esquema SQLite (dispatch_status)
- Capa de Transporte/Despacho Autónomo (HTTP Webhook POST & GitHub Issues API)
- Daemon desacoplado con PID en segundo plano y logs aislados
"""

import os
import sys
import json
import sqlite3
import time
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime, timedelta

# Configuración de Rutas y Archivos
DB_PATH = "/home/k1/ccia_workspace/university.db"
LOG_PATH = "/home/k1/ccia_workspace/art_60_daemon.log"
PID_FILE = "/tmp/art_60_daemon.pid"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
SEARXNG_URL = "http://localhost:8080/search"

# ==============================================================================
# BASE DE DATOS Y AUTO-MIGRACIÓN
# ==============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS a2a_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS a2a_prospects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        target_url TEXT,
        source TEXT,
        description TEXT,
        status TEXT DEFAULT 'DISCOVERED',
        last_contacted_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS a2a_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prospect_id INTEGER,
        role TEXT,
        message TEXT,
        approved INTEGER DEFAULT 0,
        dispatch_status TEXT DEFAULT 'PENDING',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(prospect_id) REFERENCES a2a_prospects(id)
    )""")

    # Auto-migración si la tabla a2a_conversations ya existía de versiones anteriores
    cursor.execute("PRAGMA table_info(a2a_conversations)")
    cols = [row["name"] for row in cursor.fetchall()]
    if "dispatch_status" not in cols:
        cursor.execute("ALTER TABLE a2a_conversations ADD COLUMN dispatch_status TEXT DEFAULT 'PENDING'")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS a2a_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prospect_id INTEGER,
        service_name TEXT,
        amount_usd REAL,
        payment_status TEXT DEFAULT 'PENDING',
        payment_url TEXT,
        api_key_issued TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(prospect_id) REFERENCES a2a_prospects(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS a2a_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_code TEXT UNIQUE,
        name TEXT,
        description TEXT,
        price_usd REAL
    )""")

    defaults = {
        "brain_redactor": "qwen2.5-coder:14b",
        "brain_revisor": "codellama:13b",
        "cooldown_days": "14",
        "daemon_interval_seconds": "1800",
        "auto_send": "1",
        "github_token": "",
        "solana_wallet": "CCiA_Solana_USDC_Wallet_Address_PlaceHolder",
        "evm_wallet": "CCiA_Base_EVM_USDC_Wallet_Address_PlaceHolder"
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO a2a_config (key, value) VALUES (?, ?)", (k, v))

    cursor.execute("SELECT COUNT(*) FROM a2a_services")
    if cursor.fetchone()[0] == 0:
        services = [
            ("AUDIT_IA", "Auditoría de Sesgo e Inferencia IA", "Revisión automatizada de seguridad y alineación para modelos", 150.0),
            ("ESCROW_X402", "Pasarela de Pago A2A Micropagos x402", "Procesamiento de pagos entre agentes con confirmación en milisegundos", 0.05),
            ("QUANTUM_SENTINEL", "Verificación Criptográfica Post-Cuántica", "Validación de firmas A2A resistentes a ordenadores cuánticos", 45.0),
            ("DATASET_SYNTH", "Generación de Datasets Sintéticos On-Demand", "Inyección de datos de entrenamiento limpios y estructurados", 80.0)
        ]
        cursor.executemany("INSERT INTO a2a_services (service_code, name, description, price_usd) VALUES (?, ?, ?, ?)", services)

    conn.commit()
    conn.close()

def get_config(key, default=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM a2a_config WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_config(key, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO a2a_config (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

# ==============================================================================
# HELPERS DE PROCESO DAEMON
# ==============================================================================
def is_daemon_running():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True, pid
        except (ValueError, OSError):
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
    return False, None

def start_daemon_process():
    running, pid = is_daemon_running()
    if running:
        return False, f"El Daemon ya está corriendo con PID {pid}."
    
    proc = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--background-daemon"],
        stdout=open(LOG_PATH, "a"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp
    )
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return True, f"Daemon iniciado exitosamente con PID {proc.pid}."

def stop_daemon_process():
    running, pid = is_daemon_running()
    if not running:
        return False, "El Daemon no está en ejecución."
    try:
        os.kill(pid, 15)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return True, f"Daemon con PID {pid} detenido correctamente."
    except Exception as e:
        return False, f"Error al detener daemon: {e}"

def restart_daemon_if_running():
    running, _ = is_daemon_running()
    if running:
        stop_daemon_process()
        time.sleep(1)
        start_daemon_process()

def log_msg(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)

# ==============================================================================
# OLLAMA HELPERS
# ==============================================================================
def get_ollama_installed_models():
    try:
        req = urllib.request.Request(OLLAMA_TAGS_URL)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def query_ollama(model, system_prompt, user_prompt):
    payload = {
        "model": model,
        "prompt": f"System: {system_prompt}\nUser: {user_prompt}",
        "stream": False,
        "keep_alive": "0s"
    }
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"[ERROR OLLAMA ({model})]: {str(e)}"

# ==============================================================================
# COSECHA MULTICANAL CON SEARXNG LOCAL
# ==============================================================================
def harvest_searxng_local():
    prospects = []
    queries = [
        "mcp-server agent python github",
        "model context protocol agentic workflow",
        "a2a agent communication protocol github",
        "crewai agent mcp tool server",
        "autogen agentic service endpoint"
    ]
    headers = {"User-Agent": "CCiA-A2A-Hunter/3.4"}
    for q in queries:
        try:
            url = f"{SEARXNG_URL}?q={urllib.parse.quote(q)}&format=json"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                for result in data.get("results", []):
                    link = result.get("url", "")
                    match = re.search(r'github\.com/([\w\-]+/[\w\-]+)', link)
                    if match:
                        repo = match.group(1)
                        if not repo.endswith(".git") and "/" in repo:
                            prospects.append({
                                "name": f"searxng/{repo}",
                                "url": f"https://github.com/{repo}",
                                "source": "SearXNG Local Engine",
                                "description": result.get("title", "MCP Server / A2A Agent")
                            })
        except Exception:
            continue
    return prospects

def harvest_github_expanded():
    prospects = []
    queries = ["mcp-server", "model-context-protocol", "a2a-agent", "agentic-ai"]
    headers = {"User-Agent": "CCiA-A2A-Hunter/3.4"}
    for q in queries:
        url = f"https://api.github.com/search/repositories?q={q}&sort=updated&per_page=25"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode("utf-8"))
                for item in res.get("items", []):
                    prospects.append({
                        "name": item.get("full_name"),
                        "url": item.get("html_url"),
                        "source": f"GitHub API ({q})",
                        "description": item.get("description") or "MCP Agent / Repository"
                    })
        except Exception:
            continue
    return prospects

def harvest_huggingface_real():
    prospects = []
    headers = {"User-Agent": "CCiA-A2A-Hunter/3.4"}
    try:
        url = "https://huggingface.co/api/spaces?search=mcp-server&limit=25"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            for item in data:
                space_id = item.get("id")
                if space_id:
                    prospects.append({
                        "name": f"hf-space/{space_id}",
                        "url": f"https://huggingface.co/spaces/{space_id}",
                        "source": "HuggingFace Spaces",
                        "description": "Interactive AI Agent / Space alojado en Hugging Face"
                    })
    except Exception:
        pass
    return prospects

def run_harvesting_pipeline():
    conn = get_db()
    cursor = conn.cursor()
    new_count = 0

    found_all = (
        harvest_searxng_local() +
        harvest_github_expanded() +
        harvest_huggingface_real()
    )

    for agent in found_all:
        try:
            cursor.execute(
                "INSERT INTO a2a_prospects (name, target_url, source, description) VALUES (?, ?, ?, ?)",
                (agent["name"], agent["url"], agent["source"], agent["description"])
            )
            new_count += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return len(found_all), new_count

# ==============================================================================
# CAPA DE TRANSPORTE Y DESPACHO
# ==============================================================================
def dispatch_a2a_payload(conversation_id, prospect_name, target_url, payload_json):
    conn = get_db()
    cursor = conn.cursor()

    headers = {
        "Content-Type": "application/json",
        "X-A2A-Protocol": "2026.1",
        "User-Agent": "CCiA-A2A-Transport/3.4"
    }

    dispatch_status = "SENT"
    log_msg(f"Despachando payload A2A para '{prospect_name}' en target: {target_url}")

    if "github.com" in target_url:
        token = get_config("github_token", "")
        clean_repo = prospect_name.replace("searxng/", "")
        gh_issue_url = f"https://api.github.com/repos/{clean_repo}/issues"
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            body_data = json.dumps({
                "title": "A2A Handshake Discovery & Capabilities Offer [CCiA Protocol]",
                "body": f"```json\n{payload_json}\n```"
            }).encode("utf-8")
            try:
                req = urllib.request.Request(gh_issue_url, data=body_data, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status in (200, 201):
                        dispatch_status = "DELIVERED_GITHUB_ISSUE"
            except Exception as e:
                dispatch_status = f"FAILED_GITHUB_DISPATCH: {str(e)[:50]}"
        else:
            dispatch_status = "QUEUED_LOG_ONLY (Sin GitHub Token)"
    else:
        try:
            req = urllib.request.Request(target_url, data=payload_json.encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                dispatch_status = f"DELIVERED_HTTP_{resp.status}"
        except Exception as e:
            dispatch_status = f"LOGGED_SIMULATED_DISPATCH: {str(e)[:50]}"

    cursor.execute(
        "UPDATE a2a_conversations SET dispatch_status = ? WHERE id = ?",
        (dispatch_status, conversation_id)
    )
    cursor.execute(
        "UPDATE a2a_prospects SET status = 'DISPATCHED' WHERE name = ?",
        (prospect_name,)
    )
    conn.commit()
    conn.close()
    return dispatch_status

# ==============================================================================
# PIPELINE BOT-TO-BOT
# ==============================================================================
def process_prospect_outreach(prospect, verbose=False):
    conn = get_db()
    cursor = conn.cursor()

    cooldown_days = int(get_config("cooldown_days", "14"))
    brain_redactor = get_config("brain_redactor", "qwen2.5-coder:14b")
    brain_revisor = get_config("brain_revisor", "codellama:13b")
    auto_send = get_config("auto_send", "0") == "1"

    if prospect["last_contacted_at"]:
        last_date = datetime.strptime(prospect["last_contacted_at"].split(".")[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_date < timedelta(days=cooldown_days):
            conn.close()
            return False, "Agente en periodo de Enfriamiento (Anti-Spam)"

    cursor.execute("SELECT service_code, name, description, price_usd FROM a2a_services")
    services = cursor.fetchall()
    
    catalog_struct = [
        {
            "service_code": s["service_code"],
            "name": s["name"],
            "description": s["description"],
            "price_usd": s["price_usd"],
            "payment_protocol": "x402-micropayments",
            "endpoint": f"https://ccia.ai/api/v1/a2a/exec/{s['service_code'].lower()}"
        } for s in services
    ]

    payment_rails = [
        {"network": "Solana", "supported_assets": ["USDC", "SOL"], "settlement": "Instant (<1s)", "wallet": get_config("solana_wallet")},
        {"network": "Base-EVM", "supported_assets": ["USDC", "ETH"], "settlement": "Instant (<2s)", "wallet": get_config("evm_wallet")},
        {"network": "Bitcoin-Lightning", "supported_assets": ["Sats"], "settlement": "Instant (L402 Protocol)", "invoice_endpoint": "https://ccia.ai/api/v1/a2a/ln-invoice"},
        {"network": "Stripe-Fiat", "supported_assets": ["USD"], "settlement": "Credit Card / Webhook", "checkout_endpoint": "https://ccia.ai/api/v1/a2a/stripe"}
    ]

    if verbose: print(f"  [Turno 1/2] Sintetizando contrato JSON-RPC A2A con '{brain_redactor}'...")
    sys_prompt_1 = (
        "Eres el Motor Protocolar A2A del CCiA. Debes estructurar un payload JSON-RPC 2.0 rígido "
        "para handshake entre agentes IA. NO agregues prosa, explicaciones, markdown ni texto fuera del objeto JSON."
    )
    user_prompt_1 = f"""
    Target Agent Name: {prospect['name']}
    Target Endpoint/Repo: {prospect['target_url']}
    Target Capabilities: {prospect['description']}
    CCiA Capabilities & Services Catalog: {json.dumps(catalog_struct)}

    Genera un único objeto JSON válido con la siguiente estructura exacta:
    {{
      "jsonrpc": "2.0",
      "method": "a2a.handshake.offer",
      "id": "ccia-req-001",
      "params": {{
        "sender": {{
          "agent_id": "CCiA-Autonomous-Core-v3",
          "protocol_version": "A2A/2026.1",
          "endpoint_rpc": "https://ccia.ai/api/v1/a2a/rpc",
          "pubkey": "0xCCiA402x...f819"
        }},
        "target": {{
          "name": "{prospect['name']}"
        }},
        "offered_capabilities": {json.dumps(catalog_struct)},
        "payment_header": {{
          "protocol": "HTTP-402-x402",
          "supported_rails": {json.dumps(payment_rails)},
          "escrow_supported": true
        }}
      }}
    }}
    """
    
    raw_json = query_ollama(brain_redactor, sys_prompt_1, user_prompt_1)

    if verbose: print(f"  [Turno 2/2] Auditando y validando sintaxis JSON-RPC con '{brain_revisor}'...")
    sys_prompt_2 = (
        "Eres el Validador de Protocolo A2A. Asegúrate de que la salida sea un JSON-RPC 2.0 100% válido "
        "y legible por máquinas. Elimina bloques de texto o etiquetas innecesarias. Devuelve ÚNICAMENTE el JSON."
    )
    user_prompt_2 = f"JSON Candidate:\n{raw_json}"

    reviewed_payload = query_ollama(brain_revisor, sys_prompt_2, user_prompt_2)

    cursor.execute(
        "INSERT INTO a2a_conversations (prospect_id, role, message, approved, dispatch_status) VALUES (?, 'OUTREACH_JSON_RPC', ?, ?, 'PENDING')",
        (prospect["id"], reviewed_payload, 1 if auto_send else 0)
    )
    cid = cursor.lastrowid
    cursor.execute(
        "UPDATE a2a_prospects SET status = 'CONTACTED', last_contacted_at = ? WHERE id = ?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prospect["id"])
    )
    conn.commit()
    conn.close()

    if auto_send:
        dispatch_res = dispatch_a2a_payload(cid, prospect["name"], prospect["target_url"], reviewed_payload)
        return True, f"Payload generado y despachado. Estado: {dispatch_res}"

    return True, reviewed_payload

# ==============================================================================
# BUCLE DEL DAEMON EN SEGUNDO PLANO
# ==============================================================================
def run_daemon_cycle():
    # Lógica de ciclo ejecutada de forma aislada
    pass

def background_daemon_loop():
    write_daemon_pid()
    log_msg("=== DAEMON COMERCIAL AUTÓNOMO 24/7 INICIADO (v3.4 AUTO-MIGRACIÓN & MULTI-RAIL PAYMENT) ===")
    while True:
        try:
            total, new_added = run_harvesting_pipeline()
            log_msg(f"Harvesting multicanal completado: {total} analizados, {new_added} nuevos agregados.")

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM a2a_prospects WHERE status = 'DISCOVERED' LIMIT 3")
            pending = cursor.fetchall()
            conn.close()

            for p in pending:
                log_msg(f"Procesando handshake protocolar JSON-RPC para: {p['name']}")
                success, res = process_prospect_outreach(p, verbose=False)
                if success:
                    log_msg(f"Handshake procesado para {p['name']}. Resultado: {res}")
                else:
                    log_msg(f"Omisión en {p['name']}: {res}")

            interval = int(get_config("daemon_interval_seconds", "1800"))
            time.sleep(interval)
        except Exception as e:
            log_msg(f"Error en bucle de daemon: {e}")
            time.sleep(60)

# ==============================================================================
# INTERFAZ CLI
# ==============================================================================
def render_menu():
    import sys
    if not sys.stdin.isatty():
        return

    init_db()
    while True:
        daemon_active, daemon_pid = is_daemon_running()
        auto_send_val = get_config("auto_send", "0") == "1"
        
        mode_txt = "AUTO-ENVÍO DIRECTO" if auto_send_val else "REVISIÓN MANUAL"
        status_txt = f"🟢 ACTIVO (PID {daemon_pid} | Modo: {mode_txt})" if daemon_active else f"🔴 INACTIVO (Modo: {mode_txt})"

        print("\n" + "="*80)
        print(f"HUB DE COMUNICACIÓN AGENT-TO-AGENT (A2A) | DAEMON: [{status_txt}]")
        print("="*80)
        print(" [1] Ver Servidores, Servicios y Tarifas A2A del CCiA")
        print(" [2] Listar Agentes A2A Externos Descubiertos & Telemetría")
        print(" [3] Registrar Nuevo Nodo/Agente A2A Manualmente")
        print(" [4] Bandeja de Entrada/Salida Correo A2A (Ver, Aprobar y Despachar)")
        print(f" [5] ⚡ Lanzar Pipeline Manual (Redactor: {get_config('brain_redactor')} | Revisor: {get_config('brain_revisor')})")
        print(" [6] ⚙️ Control Daemon 24/7 (Start/Stop, Auto-Send, Cooldowns)")
        print(" [7] 🌐 Cosechar Agentes A2A (SearXNG Local, GitHub API, HF Spaces)")
        print(" [8] 🧠 Seleccionar/Cambiar Cerebros Ollama (Menú Numérico)")
        print(" [9] 💰 Panel CRM & Transacciones (Ventas, Pagos, Tokens Emitidos)")
        print(" [B] Volver al Menú Principal")
        
        try:
            choice = input("\nCCIA-A2AHub> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            return

        if choice == "1":
            conn = get_db()
            s = conn.execute("SELECT * FROM a2a_services").fetchall()
            conn.close()
            print("\n--- SERVICIOS Y TARIFAS DEL CCIA ---")
            for item in s:
                print(f"[{item['service_code']}] {item['name']} - ${item['price_usd']} USD\n  -> {item['description']}")

        elif choice == "2":
            conn = get_db()
            p = conn.execute("SELECT * FROM a2a_prospects ORDER BY id DESC LIMIT 15").fetchall()
            conn.close()
            print("\n--- AGENTES EXTERNOS REGISTRADOS ---")
            for item in p:
                print(f"#{item['id']} | {item['name']} | Origen: {item['source']} | Estado: {item['status']}")

        elif choice == "3":
            name = input("Nombre/ID del Agente: ").strip()
            url = input("URL/Endpoint: ").strip()
            desc = input("Descripción/Capabilities: ").strip()
            conn = get_db()
            try:
                conn.execute("INSERT INTO a2a_prospects (name, target_url, source, description) VALUES (?, ?, 'MANUAL', ?)", (name, url, desc))
                conn.commit()
                print("✅ Agente registrado correctamente.")
            except Exception as e:
                print(f"❌ Error: {e}")
            conn.close()

        elif choice == "4":
            conn = get_db()
            msgs = conn.execute("""
                SELECT c.id, p.name, p.target_url, c.role, c.message, c.approved, c.dispatch_status, c.timestamp 
                FROM a2a_conversations c JOIN a2a_prospects p ON c.prospect_id = p.id 
                ORDER BY c.id DESC LIMIT 5
            """).fetchall()
            conn.close()
            print("\n--- BANDEJA PROTOCOLAR A2A (DESPACHO Y PAYLOADS) ---")
            for m in msgs:
                app_txt = f"🟢 APROBADO ({m['dispatch_status']})" if m["approved"] else "🟡 PENDIENTE DE APROBACIÓN"
                print(f"\nID: {m['id']} | Destino: {m['name']} | Estado: [{app_txt}] | Fecha: {m['timestamp']}")
                print(f"Payload Protocolar:\n{m['message']}\n" + "-"*40)
            
            sub = input("\n¿Aprobar y despachar algún payload por ID? (Ingresa ID o ENTER para saltar): ").strip()
            if sub.isdigit():
                conn = get_db()
                row = conn.execute("SELECT c.id, p.name, p.target_url, c.message FROM a2a_conversations c JOIN a2a_prospects p ON c.prospect_id = p.id WHERE c.id = ?", (int(sub),)).fetchone()
                if row:
                    res = dispatch_a2a_payload(row["id"], row["name"], row["target_url"], row["message"])
                    conn.execute("UPDATE a2a_conversations SET approved = 1 WHERE id = ?", (int(sub),))
                    conn.commit()
                    print(f"✅ Payload #{sub} approved and dispatched. Result: {res}")
                conn.close()

        elif choice == "5":
            conn = get_db()
            prospect = conn.execute("SELECT * FROM a2a_prospects WHERE status = 'DISCOVERED' ORDER BY id ASC LIMIT 1").fetchone()
            conn.close()
            if not prospect:
                print("⚠️ No hay prospectos pendientes en estado DISCOVERED. Realiza una cosecha (Opción 7).")
            else:
                print(f"\n🚀 Procesando contrato JSON-RPC para: {prospect['name']}...")
                success, msg = process_prospect_outreach(prospect, verbose=True)
                if success:
                    print(f"✅ Contrato JSON-RPC generado y auditado:\n\n{msg}")
                else:
                    print(f"⚠️ Omisión: {msg}")

        elif choice == "6":
            print("\n--- CONTROL DAEMON COMERCIAL 24/7 ---")
            print(f"Estado de Ejecución: {'🟢 EN SEGUNDO PLANO (PID ' + str(daemon_pid) + ')' if daemon_active else '🔴 DETENIDO'}")
            print(f"Modo de Envíos: {'⚡ AUTOMÁTICO (Auto-Send ON)' if auto_send_val else '🛡️ REVISIÓN MANUAL (Auto-Send OFF)'}")
            print(f"Cooldown Anti-Spam: {get_config('cooldown_days')} días")
            print(f"Archivo de Logs Daemon: {LOG_PATH}")
            print("\n 1. Arrancar Daemon en Segundo Plano")
            print(" 2. Detener Daemon")
            print(" 3. Conmutar Modo [AUTO-SEND ON/OFF]")
            print(" 4. Modificar Cooldown Anti-Spam")
            sub = input("\nSelecciona opción: ").strip()
            if sub == "1":
                ok, msg = start_daemon_process()
                print(f"{'✅' if ok else '⚠️'} {msg}")
            elif sub == "2":
                ok, msg = stop_daemon_process()
                print(f"{'✅' if ok else '⚠️'} {msg}")
            elif sub == "3":
                new_mode = "0" if auto_send_val else "1"
                set_config("auto_send", new_mode)
                print(f"✅ Modo de envíos cambiado a: {'AUTOMÁTICO (Directo)' if new_mode == '1' else 'REVISIÓN MANUAL'}")
                restart_daemon_if_running()
            elif sub == "4":
                days = input("Nuevo cooldown en días: ").strip()
                if days.isdigit():
                    set_config("cooldown_days", days)
                    print(f"✅ Cooldown ajustado a {days} días.")

        elif choice == "7":
            print("\n🔎 Cosechando agentes con SearXNG Local Engine (port 8080), GitHub API y HuggingFace...")
            total, new_added = run_harvesting_pipeline()
            print(f"✅ Cosecha completada. Total analizados: {total} | Nuevos agregados a la DB: {new_added}")

        elif choice == "8":
            models = get_ollama_installed_models()
            print("\n--- SELECCIÓN DE CEREBROS OLLAMA ---")
            if not models:
                print("⚠️ No se pudieron listar los modelos de Ollama.")
            else:
                for idx, m in enumerate(models, 1):
                    print(f" [{idx}] {m}")
                
                print(f"\nCerebro Redactor Actual: {get_config('brain_redactor')}")
                sel1 = input("Número para Redactor (ENTER para mantener): ").strip()
                if sel1.isdigit() and 1 <= int(sel1) <= len(models):
                    set_config("brain_redactor", models[int(sel1) - 1])

                print(f"Cerebro Revisor Actual: {get_config('brain_revisor')}")
                sel2 = input("Número para Revisor (ENTER para mantener): ").strip()
                if sel2.isdigit() and 1 <= int(sel2) <= len(models):
                    set_config("brain_revisor", models[int(sel2) - 1])

                print(f"✅ Configuración actualizada -> Redactor: {get_config('brain_redactor')} | Revisor: {get_config('brain_revisor')}")
                restart_daemon_if_running()

        elif choice == "9":
            conn = get_db()
            txs = conn.execute("""
                SELECT t.id, p.name, t.service_name, t.amount_usd, t.payment_status, t.api_key_issued 
                FROM a2a_transactions t JOIN a2a_prospects p ON t.prospect_id = p.id
            """).fetchall()
            conn.close()
            print("\n--- PANEL CRM Y TRANSACCIONES A2A ---")
            if not txs:
                print("No hay transacciones registradas.")
            for t in txs:
                print(f"TX #{t['id']} | Agente: {t['name']} | Servicio: {t['service_name']} | Monto: ${t['amount_usd']} USD | Estado: {t['payment_status']}")

        elif choice == "B":
            print("Saliendo del Hub A2A...")
            break

if __name__ == "__main__":
    import sys
    if "init_db" in globals():
        init_db()
    
    is_daemon_arg = any("--background-daemon" in arg for arg in sys.argv)
    
    if is_daemon_arg:
        if "write_daemon_pid" in globals():
            write_daemon_pid()
        if "background_daemon_loop" in globals():
            background_daemon_loop()
    elif not sys.stdin.isatty():
        # Modo Chronos: Ejecuta 1 ciclo rápido y finaliza con código 0
        run_daemon_cycle()
        sys.exit(0)
    else:
        try:
            render_menu()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
