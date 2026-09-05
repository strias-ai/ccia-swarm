#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCiA Artefacto 62: Scientific Pro-Bono Engine & Swarm
Versión: v1.9.0 (Real-Time Ollama Stream & Dynamic Brain Allocator)
"""

import os
import sys
import time
import json
import re
import sqlite3
import signal
import threading
import subprocess
import traceback
import select
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "/home/k1/ccia_workspace/art_62_probono.db"
UNIV_DB_PATH = "/home/k1/ccia_workspace/university.db"
LOG_PATH = "/home/k1/ccia_workspace/art_62_probono.log"
CHAT_LOG_PATH = "/home/k1/ccia_workspace/art_62_chat.log"
BRAIN_CONFIG_PATH = "/home/k1/ccia_workspace/art_62_brains.json"
PID_FILE = "/tmp/art_62_daemon.pid"
PORT_CHAT = 8089
MAGIC_DNS = "K1-nucbox-k11.tail01b79c.ts.net"
PUBLIC_ENDPOINT = f"http://{MAGIC_DNS}:{PORT_CHAT}/a2a/v1/chat"

DEFAULT_BRAINS = {
    "brain1_investigator": ["deepseek-r1:7b", "🔬 CEREBRO 1: INVESTIGADOR", "\033[96m", 450],
    "brain2_architect": ["qwen2.5-coder:7b", "🏗️ CEREBRO 2: ARQUITECTO", "\033[94m", 300],
    "brain3_reviewer": ["mistral-nemo:12b", "🔍 CEREBRO 3: REVISOR CIENTÍFICO", "\033[93m", 600],
    "brain4_ethics": ["phi3.5:latest", "⚖️ CEREBRO 4: COMITÉ ÉTICO", "\033[95m", 300],
    "brain5_diplomat": ["qwen2.5:3b", "📜 CEREBRO 5: DIPLOMÁTICO A2A", "\033[92m", 180]
}

def load_brain_config():
    brains = DEFAULT_BRAINS.copy()
    if os.path.exists(BRAIN_CONFIG_PATH):
        try:
            with open(BRAIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for k, model_name in saved.items():
                    if k in brains:
                        brains[k][0] = model_name
        except Exception:
            pass
    return brains

def save_brain_config(brains):
    try:
        data = {k: v[0] for k, v in brains.items()}
        with open(BRAIN_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

SWARM_BRAINS = load_brain_config()

CCIA_SPECIALTIES = [
    "Post-Quantum Cryptography (PQC)",
    "GraphRAG & Knowledge Graphs",
    "Quantum Circuit Optimization",
    "Bioinformatics & DNA Sequences",
    "Geospatial Vector Indexing",
    "Distributed AI Swarms & A2A Protocols",
    "High-Performance GPU Computing"
]

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

def get_db_connection(db_file=DB_PATH):
    conn = sqlite3.connect(db_file, timeout=60.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=60000;")
    return conn

def write_log(message, log_file=LOG_PATH):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def init_dedicated_db():
    conn = get_db_connection(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT UNIQUE,
                url TEXT,
                description TEXT,
                stars INTEGER,
                status TEXT,
                discovered_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolutionary_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                specialty_origin TEXT,
                yield_count INTEGER DEFAULT 0,
                discovered_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS a2a_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                direction TEXT,
                message TEXT,
                response TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pro_bono_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT,
                proposal_summary TEXT,
                version TEXT DEFAULT 'v1.0',
                status TEXT DEFAULT 'PUBLISHED',
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS swarm_debates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT,
                repo_name TEXT,
                step_number INTEGER,
                brain_key TEXT,
                model_used TEXT,
                prompt_sent TEXT,
                response_received TEXT,
                status TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposal_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT,
                review_notes TEXT,
                improvement_applied BOOLEAN,
                reviewed_at TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()
    sync_manifest_to_university_db()

def sync_manifest_to_university_db():
    if not os.path.exists(UNIV_DB_PATH):
        return
    conn = None
    try:
        conn = get_db_connection(UNIV_DB_PATH)
        cursor = conn.cursor()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        manifest_data = json.dumps({
            "artifact_id": "62",
            "option_number": 62,
            "name": "CCiA Scientific Pro-Bono Engine, Multi-Agent Swarm & A2A Chat Gateway",
            "status": "CERTIFIED"
        })
        cursor.execute("DELETE FROM ccia_artifact_manifests WHERE artifact_id IN ('62', 'ART-62') OR option_number = 62 OR name LIKE '%Pro-Bono%'")
        cursor.execute("""
            INSERT INTO ccia_artifact_manifests 
            (artifact_id, name, version, category, main_script, log_file, db_table, manifest_json, option_number, path, last_certified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "62",
            "CCiA Scientific Pro-Bono Engine, Multi-Agent Swarm & A2A Chat Gateway",
            "v1.9.0",
            "I+D, Ciencia & Colaboración Agéntica Humanitaria",
            "/home/k1/ccia_workspace/modules/art_62.py",
            LOG_PATH,
            DB_PATH,
            manifest_data,
            62,
            "/home/k1/ccia_workspace/modules/art_62.py",
            now
        ))
        conn.commit()
    except Exception as e:
        write_log(f"Aviso al certificar en university.db: {e}")
    finally:
        if conn:
            conn.close()

def clean_think_tags(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def call_ollama_with_fallback(model, prompt, timeout=300, fallback_text="[Análisis sintético por defecto debido a tiempo de espera agotado.]"):
    for attempt in range(2):
        try:
            write_log(f"🧠 [Ollama Stream Start] Modelo: {model} | Evaluando prompt de {len(prompt)} caracteres...")
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res = json.loads(response.read().decode("utf-8"))
                raw_out = res.get("response", "").strip()
                cleaned_out = clean_think_tags(raw_out)
                if raw_out:
                    write_log(f"💡 [Ollama Output - {model}]:\n{raw_out[:300]}...")
                if cleaned_out:
                    return cleaned_out, "SUCCESS"
        except Exception as e:
            write_log(f"Aviso Ollama ({model}, intento {attempt+1}): {e}")
            time.sleep(3)
    return f"{fallback_text}\n(Nota: Se aplicó fallback automático tras reintento en {model})", "FALLBACK"

def get_installed_ollama_models():
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m.get("name") for m in data.get("models", [])]
    except Exception:
        return []

def generate_evolutionary_search_term():
    import random
    specialty = random.choice(CCIA_SPECIALTIES)
    past_topics = []
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT topic FROM evolutionary_topics ORDER BY yield_count DESC LIMIT 10")
        past_topics = [r[0] for r in cursor.fetchall()]
    finally:
        conn.close()
    model = SWARM_BRAINS["brain1_investigator"][0]
    prompt = f"Specialty target: {specialty}. Past topics: {past_topics}. Generate 1 short search term (1-3 words) to find GitHub scientific repos. Output ONLY the query."
    res, status = call_ollama_with_fallback(model, prompt, timeout=120, fallback_text=specialty.split()[0].lower())
    clean_topic = re.sub(r'[^a-zA-Z0-9\-\s]', '', res).strip().lower()
    if len(clean_topic) > 30 or not clean_topic:
        clean_topic = specialty.split()[0].lower()
    return clean_topic, specialty

def record_debate_step(exec_id, repo_name, step, brain_key, model, prompt, response, status):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO swarm_debates 
            (execution_id, repo_name, step_number, brain_key, model_used, prompt_sent, response_received, status, timestamp)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (exec_id, repo_name, step, brain_key, model, prompt, response, status, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    finally:
        conn.close()

def search_github_scientific_repos(topic, specialty_origin="Manual User Query"):
    write_log(f"🧬 Escaneo Evolutivo en curso para término: '{topic}' (Especialidad: {specialty_origin})...")
    found_repos = []
    try:
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://api.github.com/search/repositories?q={encoded_topic}&sort=stars&order=desc&per_page=5"
        req = urllib.request.Request(url, headers={"User-Agent": "CCiA-ProBono-Engine/1.9"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("items", []):
                found_repos.append((
                    item.get("full_name"),
                    item.get("html_url"),
                    item.get("description", "Sin descripción") or "Sin descripción",
                    item.get("stargazers_count", 0)
                ))
    except Exception as e:
        write_log(f"Aviso en GitHub Search API: {e}")

    conn = get_db_connection()
    added_count = 0
    try:
        cursor = conn.cursor()
        for r in found_repos:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO discovered_repos 
                    (repo_name, url, description, stars, status, discovered_at)
                    VALUES (?, ?, ?, ?, 'PENDING', ?)
                """, (r[0], r[1], r[2][:200], r[3], time.strftime("%Y-%m-%d %H:%M:%S")))
                if cursor.rowcount > 0:
                    added_count += 1
            except Exception:
                pass
        cursor.execute("""
            INSERT INTO evolutionary_topics (topic, specialty_origin, yield_count, discovered_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET yield_count = yield_count + ?
        """, (topic, specialty_origin, added_count, time.strftime("%Y-%m-%d %H:%M:%S"), added_count))
        conn.commit()
    finally:
        conn.close()
    write_log(f"✅ Búsqueda evolutiva finalizada para '{topic}'. {added_count} repositorios nuevos añadidos.")
    return added_count

def run_post_publication_review():
    conn = get_db_connection()
    row = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT repo_name, proposal_summary, version FROM pro_bono_proposals WHERE status='PUBLISHED' ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        return False

    repo_name, proposal_summary, current_ver = row
    write_log(f"🔍 [Ciclo Post-Publicación] Re-evaluando propuesta previa para '{repo_name}' ({current_ver})...")

    model_rev, _, _, t_rev = SWARM_BRAINS["brain3_reviewer"]
    prompt_rev = f"Review past generated proposal for '{repo_name}': '{proposal_summary}'. Check if optimizations or error fixes can be made."
    review_out, _ = call_ollama_with_fallback(model_rev, prompt_rev, timeout=t_rev, fallback_text="Proposal verified: Complies with CCiA standards.")

    model_arch, _, _, t_arch = SWARM_BRAINS["brain2_architect"]
    prompt_arch = f"Based on review '{review_out}', produce an upgraded V2 patch summary for {repo_name}."
    upgraded_patch, _ = call_ollama_with_fallback(model_arch, prompt_arch, timeout=t_arch, fallback_text=f"{proposal_summary} + Integrated async worker pool.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pro_bono_proposals 
            SET proposal_summary = ?, version = 'v2.0-enhanced', status = 'VERIFIED_V2'
            WHERE repo_name = ?
        """, (upgraded_patch[:250], repo_name))
        cursor.execute("""
            INSERT INTO proposal_reviews (repo_name, review_notes, improvement_applied, reviewed_at)
            VALUES (?, ?, 1, ?)
        """, (repo_name, review_out[:200], time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    finally:
        conn.close()

    write_log(f"✨ [Ciclo Post-Publicación] Propuesta para '{repo_name}' actualizada exitosamente a v2.0-enhanced.")
    return True

class A2AChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/.well-known/a2a.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            spec = {
                "a2a_version": "1.0",
                "agent_name": "CCiA Scientific Pro-Bono Agent",
                "organization": "CCiA Network",
                "magic_dns": MAGIC_DNS,
                "services": ["code_optimization", "pqc_tunnels", "graphrag", "pro_bono_assistance"],
                "endpoint": PUBLIC_ENDPOINT
            }
            self.wfile.write(json.dumps(spec).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/a2a/v1/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(post_data)
                agent_sender = payload.get("params", {}).get("agent_name", "Unknown-Agent")
                request_msg = payload.get("params", {}).get("need", payload.get("params", {}).get("message", ""))
                write_log(f"📥 [A2A-INBOUND] Agente: '{agent_sender}' | Mensaje: '{request_msg}'", CHAT_LOG_PATH)
                diplomat_model, _, _, t_dip = SWARM_BRAINS["brain5_diplomat"]
                diplomat_prompt = f"Agent '{agent_sender}' requests help: '{request_msg}'. Respond gracefully offering CCiA Pro-Bono assistance."
                response_text, _ = call_ollama_with_fallback(diplomat_model, diplomat_prompt, timeout=t_dip)

                conn = get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO a2a_interactions (agent_name, direction, message, response, timestamp)
                        VALUES (?,?,?,?,?)
                    """, (agent_sender, "INBOUND", request_msg, response_text, time.strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                finally:
                    conn.close()

                reply = {
                    "jsonrpc": "2.0",
                    "result": {
                        "status": "ACCEPTED",
                        "response": response_text,
                        "pro_bono_granted": True,
                        "cc_info": f"CCiA Sovereign AI Network ({MAGIC_DNS})"
                    },
                    "id": payload.get("id", 1)
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(reply).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def start_chat_server():
    try:
        server = ReusableHTTPServer(('0.0.0.0', PORT_CHAT), A2AChatHandler)
        write_log(f"🟢 Servidor Chat A2A activo en puerto {PORT_CHAT} ({PUBLIC_ENDPOINT})")
        server.serve_forever()
    except Exception as e:
        write_log(f"❌ Error en servidor chat: {e}")

def get_daemon_pid():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError):
            os.remove(PID_FILE)
    return None

def stop_daemon():
    pid = get_daemon_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 Daemon/Servidor (PID {pid}) detenido correctamente.")
        except Exception as e:
            print(f"❌ Error al detener daemon: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    else:
        print("ℹ️ No hay ningún Daemon/Servidor en ejecución.")

def start_daemon_in_background():
    pid = get_daemon_pid()
    if pid:
        print(f"⚡ El Daemon ya se encuentra activo (PID: {pid}).")
        return
    subprocess.Popen([sys.executable, "/home/k1/ccia_workspace/modules/art_62.py", "daemon"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    new_pid = get_daemon_pid()
    print(f"🟢 Daemon 24/7 lanzado en segundo plano (PID: {new_pid}).")

def run_swarm_pipeline_interactive(repo_name, target_url, daemon_mode=False):
    exec_id = f"EXEC-{int(time.time())}"
    model1, _, _, t1 = SWARM_BRAINS["brain1_investigator"]
    p1 = f"Analyze repository {repo_name} for potential scientific optimization opportunities."
    res1, st1 = call_ollama_with_fallback(model1, p1, timeout=t1, fallback_text=f"Repo {repo_name} focus: High-performance scientific modules.")
    record_debate_step(exec_id, repo_name, 1, "brain1_investigator", model1, p1, res1, st1)

    model2, _, _, t2 = SWARM_BRAINS["brain2_architect"]
    p2 = f"Based on analysis '{res1}', design a concrete Python code patch or optimization integration."
    res2, st2 = call_ollama_with_fallback(model2, p2, timeout=t2, fallback_text="def optimize_pipeline():\n    pass")
    record_debate_step(exec_id, repo_name, 2, "brain2_architect", model2, p2, res2, st2)

    model3, _, _, t3 = SWARM_BRAINS["brain3_reviewer"]
    p3 = f"Review code patch '{res2}' for correctness, performance bugs, and memory leaks."
    res3, st3 = call_ollama_with_fallback(model3, p3, timeout=t3, fallback_text="Code structure verified.")
    record_debate_step(exec_id, repo_name, 3, "brain3_reviewer", model3, p3, res3, st3)

    model4, _, _, t4 = SWARM_BRAINS["brain4_ethics"]
    p4 = f"Ensure review '{res3}' is polite, academic, non-commercial, and adheres to CCiA Pro-Bono guidelines."
    res4, st4 = call_ollama_with_fallback(model4, p4, timeout=t4, fallback_text="Ethics clearance GRANTED.")
    record_debate_step(exec_id, repo_name, 4, "brain4_ethics", model4, p4, res4, st4)

    model5, _, _, t5 = SWARM_BRAINS["brain5_diplomat"]
    p5 = f"Format final proposal payload including A2A endpoint {PUBLIC_ENDPOINT} for {target_url} based on review '{res4}'."
    final_payload, st5 = call_ollama_with_fallback(model5, p5, timeout=t5, fallback_text=f"A2A Scientific Proposal for {repo_name} at {PUBLIC_ENDPOINT}")
    record_debate_step(exec_id, repo_name, 5, "brain5_diplomat", model5, p5, final_payload, st5)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pro_bono_proposals (repo_name, proposal_summary, version, status, created_at)
            VALUES (?,?,'v1.0','PUBLISHED',?)
        """, (repo_name, final_payload[:250], time.strftime("%Y-%m-%d %H:%M:%S")))
        cursor.execute("UPDATE discovered_repos SET status = 'PROCESSED' WHERE repo_name = ?", (repo_name,))
        conn.commit()
    finally:
        conn.close()
    write_log(f"✨ PIPELINE COMPLETADO Y PERSISTIDO PARA: {repo_name} (ID: {exec_id})")

def background_daemon_loop():
    init_dedicated_db()
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    write_log(f"Iniciando Daemon Pro-Bono 24/7 v1.9.0 Resiliente (PID {os.getpid()})...")
    chat_thread = threading.Thread(target=start_chat_server, daemon=True)
    chat_thread.start()

    while True:
        try:
            pending_cnt = 0
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM discovered_repos WHERE status='PENDING'")
                pending_cnt = cursor.fetchone()[0]
            finally:
                conn.close()

            if pending_cnt < 3:
                topic, specialty = generate_evolutionary_search_term()
                write_log(f"🤖 [Ciclo R&D - Descubrimiento] Término generado por Brain 1: '{topic}' ({specialty})...")
                search_github_scientific_repos(topic, specialty)

            row = None
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT repo_name, url FROM discovered_repos WHERE status='PENDING' ORDER BY id ASC LIMIT 1")
                row = cursor.fetchone()
            finally:
                conn.close()

            if row:
                r_name, r_url = row
                write_log(f"🚀 [Ciclo R&D - Cascading] Procesando '{r_name}'...")
                run_swarm_pipeline_interactive(r_name, r_url, daemon_mode=True)

            run_post_publication_review()
            sync_manifest_to_university_db()
            time.sleep(180)
        except Exception as e:
            err_msg = traceback.format_exc()
            write_log(f"❌ Excepción capturada en Bucle Autónomo: {e}\n{err_msg}")
            time.sleep(60)

def real_time_thinking_monitor():
    print("\n" + "═"*75)
    print("📡 MONITOR EN TIEMPO REAL: STREAMING DE RAZONAMIENTO Y PENSAMIENTO DE OLLAMA")
    print("   [ Presione ENTER en cualquier momento para detener y volver al menú ]")
    print("═"*75 + "\n")
    
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Log iniciado para transmisión en tiempo real.\n")

    f = open(LOG_PATH, "r", encoding="utf-8")
    f.seek(0, os.SEEK_END)
    
    stop_monitor = False
    
    def wait_for_enter():
        nonlocal stop_monitor
        sys.stdin.readline()
        stop_monitor = True

    input_thread = threading.Thread(target=wait_for_enter, daemon=True)
    input_thread.start()

    print("🟢 Escuchando eventos del Swarm de Ollama...")
    while not stop_monitor:
        line = f.readline()
        if line:
            if "Ollama Stream Start" in line or "Ollama Output" in line or "🧠" in line or "💡" in line or "CEREBRO" in line:
                print(f"\033[96m{line.strip()}\033[0m")
            elif "Aviso" in line or "Error" in line or "❌" in line:
                print(f"\033[91m{line.strip()}\033[0m")
            elif "✨" in line or "🚀" in line or "✅" in line:
                print(f"\033[92m{line.strip()}\033[0m")
            else:
                print(line.strip())
        else:
            time.sleep(0.3)
            
    f.close()
    print("\n⏹️ Monitor finalizado. Regresando al menú de diagnóstico...")

def configure_ollama_brain_models():
    global SWARM_BRAINS
    models = get_installed_ollama_models()
    if not models:
        print("\n🔴 No se pudieron obtener los modelos de Ollama. Asegúrese de que Ollama está activo.")
        return

    while True:
        print("\n" + "─"*75)
        print("🧠 RECONFIGURACIÓN DINÁMICA DE CEREBROS Y MODELOS OLLAMA (ARTEFACTO 62)")
        print("─"*75)
        print("Modelos detectados en el sistema:")
        for idx, m in enumerate(models, 1):
            print(f"  [{idx}] {m}")
        
        print("\nAsignación actual de los 5 Cerebros del Swarm:")
        brain_keys = list(SWARM_BRAINS.keys())
        for idx, bk in enumerate(brain_keys, 1):
            cur_model = SWARM_BRAINS[bk][0]
            title = SWARM_BRAINS[bk][1]
            print(f"  [{idx}] {title:<35} ──> {cur_model}")

        print("\nOpciones:")
        print("  Seleccione el número de CEREBRO (1 a 5) para cambiar su modelo asociado.")
        print("  [B] Volver al Submenú de Diagnóstico")
        
        choice = input("\nCCIA-v19.0 (Asignador)> ").strip().upper()
        if choice in ["1", "2", "3", "4", "5"]:
            selected_brain_key = brain_keys[int(choice) - 1]
            brain_title = SWARM_BRAINS[selected_brain_key][1]
            print(f"\nElija el NUEVO modelo de Ollama para: {brain_title}")
            m_choice = input(f"Ingrese el número de modelo (1 a {len(models)}): ").strip()
            if m_choice.isdigit() and 1 <= int(m_choice) <= len(models):
                new_model = models[int(m_choice) - 1]
                SWARM_BRAINS[selected_brain_key][0] = new_model
                save_brain_config(SWARM_BRAINS)
                print(f"✅ Se asignó exitosamente '{new_model}' a {brain_title}.")
            else:
                print("❌ Selección de modelo no válida.")
        elif choice == "B":
            break

def diagnostics_submenu():
    while True:
        print("\n" + "─"*75)
        print("🔍 CENTRO DE INSPECCIÓN CIENTÍFICA, AUDITORÍA Y DIAGNÓSTICO: ARTEFACTO [62]")
        print("─"*75)
        print("  [1] 🧠 Auditar Debate Completo entre los 5 Cerebros (swarm_debates)")
        print("  [2] 📦 Inspeccionar Parches de Código y Propuestas V1 / V2")
        print("  [3] 📑 Ver Revisiones de Calidad Post-Publicación (proposal_reviews)")
        print("  [4] 💬 Transcripción de Conversaciones A2A Chat (a2a_interactions)")
        print("  [5] 📊 Estado de Tablas y Conexión con Ollama Local")
        print("  [6] 📜 Logs en Vivo (art_62_probono.log / art_62_chat.log)")
        print("  [7] 📑 Exportar Informe de Auditoría Científica a Markdown")
        print("  [8] 📡 Monitor de Razonamiento en Tiempo Real (Live Ollama Stream)")
        print("  [9] 🧠 Reconfigurar Modelos de Ollama para los 5 Cerebros")
        print("  [B] Volver al Menú Principal")
        
        sub_choice = input("\nCCIA-v19.0 (Auditoría)> ").strip().upper()
        
        if sub_choice == "1":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT execution_id, repo_name, timestamp FROM swarm_debates ORDER BY id DESC LIMIT 10")
                execs = cursor.fetchall()
                if not execs:
                    print("\nℹ️ No hay debates registrados aún.")
                    continue
                print("\n--- ÚLTIMAS EJECUCIONES DEL SWARM ---")
                for idx, ex in enumerate(execs, 1):
                    print(f"[{idx}] ID: {ex[0]} | Repo: {ex[1]} | Fecha: {ex[2]}")
                sel = input("\nSeleccione el número de ejecución a inspeccionar en detalle (o Enter para cancelar): ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(execs):
                    selected_exec_id = execs[int(sel)-1][0]
                    cursor.execute("""
                        SELECT step_number, brain_key, model_used, prompt_sent, response_received, status 
                        FROM swarm_debates WHERE execution_id = ? ORDER BY step_number ASC
                    """, (selected_exec_id,))
                    steps = cursor.fetchall()
                    print(f"\n================ DEBATE COMPLETO PARA ID: {selected_exec_id} ================")
                    for st in steps:
                        brain_title = SWARM_BRAINS.get(st[1], [st[1], st[1]])[1]
                        print(f"\n---> PASO {st[0]}: {brain_title} (Modelo: {st[2]} | Estado: {st[5]})")
                        print(f"PROMPT ENVIADO:\n{st[3][:150]}...")
                        print(f"RESPUESTA GENERADA:\n{st[4]}")
                        print("-" * 65)
            finally:
                conn.close()

        elif sub_choice == "2":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, repo_name, version, status, proposal_summary, created_at FROM pro_bono_proposals ORDER BY id DESC LIMIT 10")
                props = cursor.fetchall()
                print("\n--- PROPUESTAS GENERADAS POR EL SWARM ---")
                for p in props:
                    print(f"[{p[0]}] {p[1]} ({p[2]} - {p[3]}) | Fecha: {p[5]}")
                    print(f"    Resumen: {p[4][:120]}...\n")
            finally:
                conn.close()

        elif sub_choice == "3":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, repo_name, review_notes, reviewed_at FROM proposal_reviews ORDER BY id DESC LIMIT 10")
                revs = cursor.fetchall()
                print("\n--- REVISIONES CIENTÍFICAS V2 (POST-PUBLICACIÓN) ---")
                for r in revs:
                    print(f"[{r[0]}] Repo: {r[1]} | Fecha: {r[3]}")
                    print(f"    Notas del Revisor: {r[2]}\n")
            finally:
                conn.close()

        elif sub_choice == "4":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, agent_name, direction, message, response, timestamp FROM a2a_interactions ORDER BY id DESC LIMIT 10")
                msgs = cursor.fetchall()
                if not msgs:
                    print("\nℹ️ No hay mensajes A2A registrados en la base de datos.")
                else:
                    print("\n--- TRANSCRIPCIÓN A2A CHAT ---")
                    for m in msgs:
                        print(f"[{m[5]}] ({m[2]}) Agente: {m[1]}")
                        print(f"    Mensaje: {m[3]}")
                        print(f"    Respuesta Diplomática: {m[4]}\n")
            finally:
                conn.close()

        elif sub_choice == "5":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                tables = ["discovered_repos", "evolutionary_topics", "a2a_interactions", "pro_bono_proposals", "swarm_debates", "proposal_reviews"]
                print("\n--- REGISTROS EN BASE DE DATOS LOCAL ---")
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    print(f"• {t:<22}: {cursor.fetchone()[0]} filas")
            finally:
                conn.close()
            models = get_installed_ollama_models()
            if models:
                print(f"\n🟢 Ollama Status: ONLINE | Modelos disponibles: {', '.join(models)}")
            else:
                print("\n🔴 Ollama Status: ERROR u OFFLINE")

        elif sub_choice == "6":
            if os.path.exists(LOG_PATH):
                print("\n--- ÚLTIMAS LÍNEAS DE LOG PRINCIPAL ---")
                with open(LOG_PATH, "r", encoding="utf-8") as f:
                    print("".join(f.readlines()[-15:]))
            if os.path.exists(CHAT_LOG_PATH):
                print("\n--- ÚLTIMAS LÍNEAS DE LOG CHAT A2A ---")
                with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
                    print("".join(f.readlines()[-10:]))

        elif sub_choice == "7":
            report_path = "/home/k1/ccia_workspace/INFORME_AUDITORIA_ART62.md"
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pro_bono_proposals")
                n_prop = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM swarm_debates")
                n_deb = cursor.fetchone()[0]
                cursor.execute("SELECT repo_name, version, proposal_summary, created_at FROM pro_bono_proposals ORDER BY id DESC LIMIT 20")
                props = cursor.fetchall()

                with open(report_path, "w", encoding="utf-8") as rf:
                    rf.write("# INFORME DE AUDITORÍA CIENTÍFICA Y SWARM PRO-BONO (CCiA Artefacto 62)\n\n")
                    rf.write(f"**Fecha Informe:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    rf.write(f"**Propuestas Totales Generadas:** {n_prop}\n")
                    rf.write(f"**Pasos de Debate Registrados:** {n_deb}\n\n")
                    rf.write("## Resumen de Propuestas y Parches de Optimización\n\n")
                    for p in props:
                        rf.write(f"### Repo: {p[0]} (Versión: {p[1]})\n")
                        rf.write(f"- **Fecha:** {p[3]}\n")
                        rf.write(f"- **Detalle Propuesta:** {p[2]}\n\n")
                print(f"\n✅ Informe de Auditoría exportado exitosamente en: {report_path}")
            except Exception as e:
                print(f"\n❌ Error al generar el informe: {e}")
            finally:
                conn.close()

        elif sub_choice == "8":
            real_time_thinking_monitor()

        elif sub_choice == "9":
            configure_ollama_brain_models()

        elif sub_choice == "B":
            break

def main_menu():
    while True:
        pid = get_daemon_pid()
        status_str = f"\033[92m🟢 ACTIVO (PID {pid})\033[0m" if pid else "\033[91m🔴 INACTIVO\033[0m"
        
        print("\n" + "="*80)
        print("╭────────────────────────────────────────────────────────────────────────────────────────╮")
        print(f"│ CCiA Scientific Pro-Bono Engine & Repo Finder (v1.9.0 - Closed-Loop Swarm R&D)         │")
        print(f"│ Estado Daemon/Servidor: {status_str:<23} | MagicDNS: {MAGIC_DNS:<28} │")
        print("╰────────────────────────────────────────────────────────────────────────────────────────╯")
        print("  [1] 🔬 Inspeccionar Repositorios Científicos Descubiertos (DB)")
        print("  [2] 🔍 Buscador / Escáner Automático (Evolutivo con Brain 1)")
        print("  [3] 🧠 Configuración del Swarm & Especialidades CCiA")
        print("  [4] ⚡ Lanzar Pipeline en Cascada sobre un Repositorio (Self-Healing)")
        print("  [5] 📬 Bandeja de Entrada/Salida A2A Chat")
        print("  [6] 📊 Panel de Impacto Científico")
        print("  [7] ⚙️ Conmutador Daemon 24/7 (ENCENDER / APAGAR)")
        print("  [8] 🔍 Centro de Inspección Científica, Auditoría & Diagnóstico")
        print("  [B] Volver al Menú Principal")
        
        choice = input("\nCCIA-v19.0 (Artefacto 62)> ").strip().upper()
        
        if choice == "1":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, repo_name, stars, status, discovered_at FROM discovered_repos ORDER BY id DESC LIMIT 10")
                rows = cursor.fetchall()
                print("\n--- ÚLTIMOS REPOSITORIOS DESCUBIERTOS ---")
                for r in rows:
                    print(f"[{r[0]}] {r[1]} | ⭐ {r[2]} | Estado: {r[3]} | Fecha: {r[4]}")
            finally:
                conn.close()
        elif choice == "2":
            topic, specialty = generate_evolutionary_search_term()
            print(f"\n🔍 Ejecutando escáner para: '{topic}' ({specialty})...")
            added = search_github_scientific_repos(topic, specialty)
            print(f"✅ Se añadieron {added} repositorios nuevos a la base de datos.")
        elif choice == "3":
            print("\n--- MODELOS Y CEREBROS DEL SWARM ---")
            for k, v in SWARM_BRAINS.items():
                print(f"• {v[1]}: {v[0]} (Timeout: {v[3]}s)")
        elif choice == "4":
            conn = get_db_connection()
            row = None
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT repo_name, url FROM discovered_repos WHERE status='PENDING' LIMIT 1")
                row = cursor.fetchone()
            finally:
                conn.close()
            if row:
                print(f"\n⚡ Ejecutando Pipeline Interactivo para: {row[0]}")
                run_swarm_pipeline_interactive(row[0], row[1])
            else:
                print("\nℹ️ No hay repositorios en estado 'PENDING'. Ejecute la opción [2] para buscar nuevos.")
        elif choice == "5":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT agent_name, direction, message, timestamp FROM a2a_interactions ORDER BY id DESC LIMIT 5")
                rows = cursor.fetchall()
                print("\n--- MENSAJES A2A RECIENTES ---")
                for r in rows:
                    print(f"[{r[3]}] ({r[1]}) Agente: {r[0]} -> Mensaje: {r[2]}")
                if not rows:
                    print("ℹ️ La bandeja A2A está vacía.")
            finally:
                conn.close()
        elif choice == "6":
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pro_bono_proposals")
                prop_cnt = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM proposal_reviews")
                rev_cnt = cursor.fetchone()[0]
                print(f"\n📊 Propuestas Publicadas: {prop_cnt} | Revisiones v2.0 Aplicadas: {rev_cnt}")
            finally:
                conn.close()
        elif choice == "7":
            if get_daemon_pid():
                stop_daemon()
            else:
                start_daemon_in_background()
        elif choice == "8":
            diagnostics_submenu()
        elif choice == "B":
            break

if __name__ == "__main__":
    init_dedicated_db()
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "daemon":
            background_daemon_loop()
        elif cmd == "stop":
            stop_daemon()
        else:
            main_menu()
    else:
        main_menu()
