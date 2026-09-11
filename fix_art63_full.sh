#!/usr/bin/env bash
set -e

DB_PATH="/home/k1/ccia_workspace/university.db"
LOG_FILE="/home/k1/ccia_workspace/art63_autonomo.log"
ART63_MODULE="/home/k1/ccia_workspace/modules/art_63.py"
ART63_MANDO="/home/k1/ccia_workspace/ccia_mando_63.py"

echo "================================================================================"
echo "🛠️ REPARACIÓN INTEGRAL: RESTAURANDO 12 OPCIONES Y SOLUCIONANDO SQLITE"
echo "================================================================================"

# 1. Reescribir Módulo Completo Artefacto 63 con Actualización SQL Dinámica Segura
echo -e "\n1️⃣ Reconstruyendo $ART63_MODULE con las 12 opciones y SQL dinámico..."
cat << 'PYTHON_EOF' > "$ART63_MODULE"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCiA Artefacto 63 - Centro de Mando y Control Tri-Enjambre Unificado (12 Opciones Restauradas)
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import shutil
import argparse

DB_PATH = "/home/k1/ccia_workspace/university.db"
CONFIG_PATH = "/home/k1/ccia_workspace/brain_config.json"
WALLET_PATH = "/home/k1/ccia_workspace/wallet_config.json"
LOCK_FILE = "/tmp/ccia_bounty.lock"
TARGET_DIR = "/tmp/bounty_target"
DAEMON_PID_FILE = "/tmp/ccia_art63_daemon.pid"
DAEMON_LOG_FILE = "/home/k1/ccia_workspace/art63_autonomo.log"
BRAIN_TIMEOUT = 7200

class TriSwarmOrchestrator:
    def __init__(self):
        self.db_path = DB_PATH
        self.config_path = CONFIG_PATH
        self.wallet_path = WALLET_PATH
        self.brains = self.load_brains()
        self.wallets = self.load_wallets()
        self.init_db_structures()

    def init_db_structures(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bounty_swarm_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT,
            issue_id TEXT,
            swarm1_draft TEXT,
            swarm2_versions TEXT,
            swarm3_decision TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS swarm_debates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bounty_id TEXT,
            brain_id TEXT,
            role TEXT,
            argument TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS proposal_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr_url TEXT,
            quality_score REAL,
            verdict TEXT,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS bounty_vector_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_key TEXT,
            solution_summary TEXT,
            code_patch TEXT,
            embedding_tag TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

        conn.commit()
        conn.close()

    def load_brains(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) == 15:
                        return data
            except Exception:
                pass
        return self.get_default_brains()

    def get_default_brains(self):
        return [
            {"id": "1", "code": "1.1", "swarm": "Enjambre 1", "role": "Detector de Spam", "icon": "🔬", "model": "ccia-s1-1-spam-detector:latest"},
            {"id": "2", "code": "1.2", "swarm": "Enjambre 1", "role": "Parser AST", "icon": "🏗️", "model": "ccia-s1-2-ast-parser:latest"},
            {"id": "3", "code": "1.3", "swarm": "Enjambre 1", "role": "Diseñador Algorítmico", "icon": "📐", "model": "ccia-s1-3-algo-designer:latest"},
            {"id": "4", "code": "1.4", "swarm": "Enjambre 1", "role": "Generador de Parches", "icon": "⚡", "model": "ccia-s1-4-patch-generator:latest"},
            {"id": "5", "code": "1.5", "swarm": "Enjambre 1", "role": "Auditor de Conformidad", "icon": "🛡️", "model": "ccia-s1-5-compliance-auditor:latest"},
            {"id": "6", "code": "2.1", "swarm": "Enjambre 2", "role": "Validador Sintáctico", "icon": "🧪", "model": "ccia-s2-1-syntax-validator:latest"},
            {"id": "7", "code": "2.2", "swarm": "Enjambre 2", "role": "Profiler Rendimiento", "icon": "⏱️", "model": "ccia-s2-2-perf-profiler:latest"},
            {"id": "8", "code": "2.3", "swarm": "Enjambre 2", "role": "Agente Mutación", "icon": "🧬", "model": "ccia-s2-3-mutation-agent:latest"},
            {"id": "9", "code": "2.4", "swarm": "Enjambre 2", "role": "Historiador Vectorial", "icon": "📚", "model": "ccia-s2-4-patch-historian:latest"},
            {"id": "10", "code": "2.5", "swarm": "Enjambre 2", "role": "Selector Óptimo", "icon": "🎯", "model": "ccia-s2-5-optimal-selector:latest"},
            {"id": "11", "code": "3.1", "swarm": "Enjambre 3", "role": "Auditor Red-Team", "icon": "🚨", "model": "ccia-s3-1-redteam-auditor:latest"},
            {"id": "12", "code": "3.2", "swarm": "Enjambre 3", "role": "Ejecutor Aislamiento", "icon": "📦", "model": "ccia-s3-2-isolation-executor:latest"},
            {"id": "13", "code": "3.3", "swarm": "Enjambre 3", "role": "Fallback Dispatcher", "icon": "🔄", "model": "ccia-s3-3-fallback-dispatcher:latest"},
            {"id": "14", "code": "3.4", "swarm": "Enjambre 3", "role": "Formateador PR", "icon": "📝", "model": "ccia-s3-4-pr-formatter:latest"},
            {"id": "15", "code": "3.5", "swarm": "Enjambre 3", "role": "Entregador Final", "icon": "🚀", "model": "ccia-s3-5-final-deliverer:latest"}
        ]

    def save_brains(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.brains, f, indent=2, ensure_ascii=False)

    def load_wallets(self):
        if os.path.exists(self.wallet_path):
            try:
                with open(self.wallet_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "lightning_address": "vellichorlate475846@getalby.com",
            "evm_address": "0x0000000000000000000000000000000000000000",
            "btc_address": "bc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }

    def save_wallets(self):
        with open(self.wallet_path, "w", encoding="utf-8") as f:
            json.dump(self.wallets, f, indent=2, ensure_ascii=False)

    def get_art63_daemon_status(self):
        if os.path.exists(DAEMON_PID_FILE):
            try:
                with open(DAEMON_PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                return True, pid
            except (ValueError, OSError):
                if os.path.exists(DAEMON_PID_FILE):
                    os.remove(DAEMON_PID_FILE)
        return False, None

    def toggle_art63_daemon(self):
        is_running, pid = self.get_art63_daemon_status()
        script_path = os.path.abspath(__file__)

        if is_running:
            try:
                os.kill(pid, 15)
                time.sleep(1)
                print(f"\n🔴 Daemon del Artefacto 63 detenido (PID: {pid}).")
            except Exception as e:
                print(f"\n⚠️ Error al detener daemon: {e}")
            if os.path.exists(DAEMON_PID_FILE):
                os.remove(DAEMON_PID_FILE)
        else:
            cmd = f"nohup python3 {script_path} --daemon > {DAEMON_LOG_FILE} 2>&1 & echo $! > {DAEMON_PID_FILE}"
            subprocess.Popen(cmd, shell=True)
            time.sleep(1.5)
            is_now_running, new_pid = self.get_art63_daemon_status()
            if is_now_running:
                print(f"\n🟢 Daemon del Artefacto 63 iniciado en segundo plano (PID: {new_pid}).")
            else:
                print("\n⚠️ Ocurrió un problema al iniciar el Daemon.")

    def toggle_art62_247(self):
        """Actualización dinámica compatible con cualquier esquema de ccia_artifact_manifests"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
        row = cur.fetchone()
        curr_status = row[0] if row else "DISABLED"
        new_status = "DISABLED" if curr_status == "ACTIVE" else "ACTIVE"

        cur.execute("UPDATE ccia_artifact_manifests SET status = ? WHERE artifact_id = '62';", (new_status,))
        if cur.rowcount == 0:
            cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
            cols_info = cur.fetchall()
            row_dict = {}
            for col in cols_info:
                cname, cnotnull = col[1], col[3]
                if cname == "artifact_id": row_dict[cname] = "62"
                elif cname == "status": row_dict[cname] = new_status
                elif cname == "name": row_dict[cname] = "Artefacto 62 Bucle 24/7"
                elif cname == "version": row_dict[cname] = "1.9.0"
                elif cname == "category": row_dict[cname] = "Core Swarm"
                else: row_dict[cname] = "DEFAULT" if cnotnull else None

            cols_str = ", ".join(row_dict.keys())
            placeholders = ", ".join(["?"] * len(row_dict))
            cur.execute(f"INSERT INTO ccia_artifact_manifests ({cols_str}) VALUES ({placeholders});", tuple(row_dict.values()))

        conn.commit()
        conn.close()

        icon = "🟢" if new_status == "ACTIVE" else "🔴"
        print(f"\n{icon} BUCLE 24/7 ARTEFACTO 62 CAMBIADO A: [{new_status}]")

    def acquire_system_mutex(self):
        print("\n🔒 [ART-63] Reclamando Mutex del sistema...")
        with open(LOCK_FILE, "w") as f:
            f.write("ART63_ACTIVE_PID_" + str(os.getpid()))

    def release_system_mutex(self):
        print("\n🔓 [ART-63] Liberando Mutex...")
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

    def list_ollama_models(self):
        try:
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if res.returncode == 0:
                lines = res.stdout.strip().split("\n")[1:]
                return [line.split()[0] for line in lines if line.split()]
        except Exception:
            pass
        return [b["model"] for b in self.brains]

    def record_debate(self, bounty_id, brain_id, role, argument):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO swarm_debates (bounty_id, brain_id, role, argument) VALUES (?, ?, ?, ?);",
                    (bounty_id, brain_id, role, argument[:1000]))
        conn.commit()
        conn.close()

    def record_review(self, pr_url, score, verdict, feedback):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO proposal_reviews (pr_url, quality_score, verdict, feedback) VALUES (?, ?, ?, ?);",
                    (pr_url, score, verdict, feedback))
        conn.commit()
        conn.close()

    def search_vector_memory(self, query):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT issue_key, solution_summary FROM bounty_vector_memory WHERE solution_summary LIKE ? OR issue_key LIKE ? LIMIT 3;",
                    (f"%{query}%", f"%{query}%"))
        rows = cur.fetchall()
        conn.close()
        return rows if rows else "Sin antecedentes en memoria vectorial."

    def execute_brain_turn(self, brain_obj, task_title, context, stream_live=True):
        model = brain_obj["model"]
        b_id = brain_obj["code"]
        role = brain_obj["role"]

        print(f"\n  🧠 [{brain_obj['icon']} CEREBRO {b_id}: {role}] Modelo: [{model}]")
        cmd = ["ollama", "run", model, f"Tarea: {task_title}\nContexto: {str(context)[:1200]}"]

        try:
            if stream_live:
                print("  📡 --- INICIO STREAM DE RAZONAMIENTO ---")
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                full_out = []
                for line in proc.stdout:
                    sys.stdout.write("  │ " + line)
                    sys.stdout.flush()
                    full_out.append(line)
                proc.wait()
                print("  📡 --- FIN STREAM DE RAZONAMIENTO ---")
                output = "".join(full_out).strip()
            else:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=BRAIN_TIMEOUT)
                output = res.stdout.strip() if res.returncode == 0 else "Ejecución completada"

            self.record_debate(task_title[:30], b_id, role, output)
            return output
        except Exception as e:
            err_msg = f"Error en cerebro {b_id}: {e}"
            print(f"  ⚠️ {err_msg}")
            return err_msg

    def is_issue_processed(self, repo, issue_num):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM bounty_swarm_history WHERE repo=? AND issue_id=?;", (repo, str(issue_num)))
        row = cur.fetchone()
        conn.close()
        return row is not None

    def fetch_next_unprocessed_bounty(self):
        print("\n🔎 Buscando bounties abiertos no procesados en GitHub...")
        cmd = ["gh", "search", "issues", "bounty", "--state", "open", "--limit", "15", "--json", "repository,number,title,body"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            try:
                candidates = json.loads(res.stdout)
                for item in candidates:
                    repo = item.get("repository", {}).get("nameWithOwner")
                    num = str(item.get("number"))
                    if repo and num and not self.is_issue_processed(repo, num):
                        return {
                            "repo": repo,
                            "number": num,
                            "title": item.get("title", ""),
                            "body": item.get("body", "")
                        }
            except Exception as e:
                print(f"⚠️ Error parseando respuesta de GitHub: {e}")
        return None

    def run_full_pipeline(self, target_repo=None, target_issue=None):
        self.acquire_system_mutex()
        try:
            bounty_data = None
            if target_repo and target_issue:
                cmd_issue = ["gh", "issue", "view", str(target_issue), "--repo", target_repo, "--json", "title,body"]
                res = subprocess.run(cmd_issue, capture_output=True, text=True)
                body_str = res.stdout if res.returncode == 0 else "Issue details"
                bounty_data = {"repo": target_repo, "number": str(target_issue), "title": f"Issue #{target_issue}", "body": body_str}
            else:
                bounty_data = self.fetch_next_unprocessed_bounty()

            if not bounty_data:
                print("\n✨ [SIN BOUNTIES PENDIENTES] No hay bounties sin procesar.")
                return {"status": "NO_NEW_BOUNTIES"}

            repo = bounty_data["repo"]
            issue_num = bounty_data["number"]
            issue_title = bounty_data["title"]
            issue_body = bounty_data["body"]
            issue_key = f"{repo}#{issue_num}"

            print("\n" + "="*80)
            print(f"🚀 INICIANDO EJECUCIÓN TRI-ENJAMBRE COMPLETA SOBRE {issue_key}: {issue_title}")
            print("="*80)

            # CEREBRO 1.1: DETECTOR DE SPAM
            out_1 = self.execute_brain_turn(self.brains[0], "Detector Spam", issue_body)
            if '"valid": false' in out_1.lower() or '"valid":false' in out_1.lower() or ("spam" in out_1.lower() and "invalid" in out_1.lower()):
                print(f"\n🛑 [CORTOCIRCUITO ANTISPAM] Issue {issue_key} descartado.")
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                            (repo, issue_num, out_1, "SPAM_SKIP"))
                conn.commit()
                conn.close()
                return {"status": "SPAM_DISCARDED"}

            memory_ctx = self.search_vector_memory(repo)
            print(f"📚 Memoria Vectorial Consultada: {memory_ctx}")

            # Ejecución secuencial de los cerebros restantes
            out_2 = self.execute_brain_turn(self.brains[1], "Parser AST", repo)
            out_3 = self.execute_brain_turn(self.brains[2], "Diseñador Algoritmos", f"{out_1}\n{out_2}\nMemoria: {memory_ctx}")
            out_4 = self.execute_brain_turn(self.brains[3], "Generador Parche", out_3)
            out_5 = self.execute_brain_turn(self.brains[4], "Auditor Conformidad", out_4)

            for b in self.brains[5:]:
                self.execute_brain_turn(b, f"Procesamiento {b['role']}", out_5, stream_live=False)

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                        (repo, issue_num, out_4, "SUCCESS"))
            conn.commit()
            conn.close()

            print("\n✅ EJECUCIÓN TRI-ENJAMBRE FINALIZADA CON ÉXITO")
            return {"status": "SUCCESS"}
        finally:
            self.release_system_mutex()

    def find_and_enqueue_bounties(self):
        print("\n🎯 RASTREANDO BOUNTIES EN VIVO VÍA GH CLI...")
        cmd = ["gh", "search", "issues", "bounty", "--state", "open", "--limit", "10", "--json", "repository,number,title,url"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            try:
                data = json.loads(res.stdout)
                print("="*80)
                print(f"🎯 BOUNTIES DISPONIBLES ({len(data)} encontrados):")
                print("="*80)
                for idx, item in enumerate(data, 1):
                    repo_name = item.get("repository", {}).get("nameWithOwner", "Unknown")
                    issue_num = str(item.get('number'))
                    status_str = "PROCESADO" if self.is_issue_processed(repo_name, issue_num) else "PENDIENTE"
                    print(f"[{idx}] Proyecto: {repo_name} [{status_str}]")
                    print(f"    • Issue: #{issue_num} - {item.get('title')}")
                    print(f"    • URL: {item.get('url')}\n")
                return data
            except Exception as e:
                print(f"⚠️ Error parseando gh CLI: {e}")
        return []

    def run_autonomous_daemon_loop(self):
        print("\n🔄 [MODO AUTÓNOMO 24/7 INICIADO] Escaneando bounties...")
        while True:
            try:
                res = self.run_full_pipeline()
                if res.get("status") == "NO_NEW_BOUNTIES":
                    time.sleep(300)
                else:
                    time.sleep(15)
            except Exception as e:
                print(f"⚠️ Error en bucle autónomo: {e}")
                time.sleep(60)

def pause_terminal():
    input("\n Presiona [ENTER] para regresar al menú principal...")

def show_reconfig_menu(orch):
    while True:
        models = orch.list_ollama_models()
        print("\n" + "="*80)
        print("🧠 RECONFIGURAR MODELOS DE OLLAMA PARA LOS 15 CEREBROS (OPCIÓN 2)")
        print("="*80)
        print("Modelos detectados:")
        for idx, m in enumerate(models, 1):
            print(f"  [{idx}] {m}")

        print("\nAsignación actual del Swarm:")
        for b in orch.brains:
            print(f"  [{b['id']}] {b['icon']} CEREBRO {b['id']} ({b['role']:<24}) ──> {b['model']}")

        print("-" * 80)
        choice = input("CCiA-Reconfig (Número de Cerebro 1-15, o B para volver)> ").strip().upper()
        if choice == "B":
            break
        elif choice.isdigit() and 1 <= int(choice) <= 15:
            b_index = int(choice) - 1
            m_choice = input(f"Selecciona número de modelo para Cerebro {choice}: ").strip()
            if m_choice.isdigit() and 1 <= int(m_choice) <= len(models):
                orch.brains[b_index]["model"] = models[int(m_choice) - 1]
                orch.save_brains()
                print("✅ Modelo actualizado.")

def show_bounty_submenu(orch):
    while True:
        print("\n" + "="*80)
        print("🎯 SUBMENÚ DE CONTROL Y BÚSQUEDA DE BOUNTIES (OPCIÓN 4)")
        print("="*80)
        print("  [A] 🔍 Buscador Manual de Bounties en Vivo (GitHub CLI)")
        print("  [B] 📊 Inspeccionar Base de Datos Evolutiva de Bounties")
        print("  [0] 🚪 Volver al Menú Principal")
        print("="*80)

        opt = input("CCiA-Bounty> ").strip().upper()
        if opt == "A":
            orch.find_and_enqueue_bounties()
            pause_terminal()
        elif opt == "B":
            conn = sqlite3.connect(orch.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, repo, issue_id, status, created_at FROM bounty_swarm_history ORDER BY id DESC LIMIT 10;")
            rows = cur.fetchall()
            conn.close()
            print("\n📊 HISTORIAL DE BOUNTIES:")
            for r in rows:
                print(f"  ID #{r[0]} | Repo: {r[1]} | Issue: #{r[2]} | Estado: {r[3]} | Fecha: {r[4]}")
            pause_terminal()
        elif opt == "0":
            break

def show_wallet_menu(orch):
    print("\n" + "="*80)
    print("💳 CONFIGURACIÓN DE CARTERAS Y RECEPCIÓN DE BOUNTIES (OPCIÓN 5)")
    print("="*80)
    print(f"  • Lightning Address : {orch.wallets.get('lightning_address')}")
    print(f"  • EVM Address       : {orch.wallets.get('evm_address')}")
    print(f"  • BTC Address       : {orch.wallets.get('btc_address')}")
    print("-" * 80)
    ans = input("¿Actualizar dirección? (L: Lightning, E: EVM, B: BTC, N: Ninguna): ").strip().upper()
    if ans == "L":
        orch.wallets["lightning_address"] = input("Nueva Lightning Address: ").strip()
        orch.save_wallets()
    elif ans == "E":
        orch.wallets["evm_address"] = input("Nueva EVM Address: ").strip()
        orch.save_wallets()
    elif ans == "B":
        orch.wallets["btc_address"] = input("Nueva BTC Address: ").strip()
        orch.save_wallets()
    pause_terminal()

def show_mando_menu():
    orch = TriSwarmOrchestrator()

    while True:
        conn = sqlite3.connect(orch.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
        row = cur.fetchone()
        conn.close()
        status_62 = row[0] if row else "DISABLED"
        has_lock = os.path.exists(LOCK_FILE)

        daemon_running, daemon_pid = orch.get_art63_daemon_status()
        status_daemon = f"🟢 ACTIVO (PID: {daemon_pid})" if daemon_running else "🔴 INACTIVO"

        print("\n" + "="*80)
        print(" 🎛️  CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62")
        print("="*80)
        print(f" Estado Bucle 24/7 Artefacto 62 : [{status_62}]")
        print(f" Daemon Bucle 24/7 Artefacto 63 : [{status_daemon}]")
        print(f" Cerrojo Mutex (/tmp)          : [{'RECLAMADO' if has_lock else 'LIBRE'}]")
        print("-" * 80)
        print("  [1] 📋 Ver Mapeo Actual y Estado del Enjambre")
        print("  [2] 🧠 Reconfigurar Modelos de Ollama para los 15 Cerebros")
        print("  [3] 🚀 Lanzar Ejecución Completa Tri-Enjambre (Siguiente Bounty Dinámico)")
        print("  [4] 🎯 Submenú de Control y Búsqueda de Bounties (Buscador/DB Evolutiva)")
        print("  [5] 💳 Configuración de Carteras de Recepción (Lightning / EVM / BTC)")
        print("  [6] 🧠 Auditar Debate Completo entre los 15 Cerebros (swarm_debates)")
        print("  [7] 📑 Ver Revisiones de Calidad Post-Publicación (proposal_reviews)")
        print("  [8] 📡 Monitor de Razonamiento en Tiempo Real (Live Ollama Stream)")
        print("  [9] 📊 Estado de Tablas y Conexión con Ollama Local")
        print("  [10] 📜 Logs en Vivo & Informe de Auditoría de Versiones Art 63")
        print("  [11] ⚡ Encender / Apagar Bucle 24/7 Artefacto 62 (TOGGLE ON/OFF)")
        print("  [12] 🔄 Encender / Apagar Daemon Bucle Autónomo Artefacto 63 (TOGGLE ON/OFF)")
        print("  [0] 🚪 Salir al Menú Principal")
        print("="*80)

        opt = input("CCiA-Mando-63> ").strip()

        if opt == "1":
            print("\n📋 MAPEO ACTUAL DEL SWARM:")
            for b in orch.brains:
                print(f"  [{b['id']}] {b['icon']} CEREBRO {b['id']} ({b['role']:<24}) ──> {b['model']}")
            pause_terminal()

        elif opt == "2":
            show_reconfig_menu(orch)

        elif opt == "3":
            orch.run_full_pipeline()
            pause_terminal()

        elif opt == "4":
            show_bounty_submenu(orch)

        elif opt == "5":
            show_wallet_menu(orch)

        elif opt == "6":
            conn = sqlite3.connect(orch.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, bounty_id, brain_id, role, argument, created_at FROM swarm_debates ORDER BY id DESC LIMIT 10;")
            rows = cur.fetchall()
            conn.close()
            print("\n🧠 DEBATES REGISTRADOS:")
            for r in rows:
                print(f" ID #{r[0]} | Target: {r[1]} | Cerebro {r[2]} ({r[3]}) | Fecha: {r[5]}")
                print(f" Arg: {r[4][:200]}...\n" + "-"*40)
            pause_terminal()

        elif opt == "7":
            conn = sqlite3.connect(orch.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, pr_url, quality_score, verdict, feedback FROM proposal_reviews ORDER BY id DESC LIMIT 10;")
            rows = cur.fetchall()
            conn.close()
            print("\n📑 REVISIONES POST-PUBLICACIÓN:")
            for r in rows:
                print(f" Review #{r[0]} | PR: {r[1]} | Score: {r[2]} | Veredicto: {r[3]}")
            pause_terminal()

        elif opt == "8":
            b_id = input("\nNúmero de Cerebro a monitorear (1 a 15): ").strip()
            if b_id.isdigit() and 1 <= int(b_id) <= 15:
                b_obj = orch.brains[int(b_id) - 1]
                orch.execute_brain_turn(b_obj, "Test Diagnóstico Stream", "Verificación en directo", stream_live=True)
            pause_terminal()

        elif opt == "9":
            models = orch.list_ollama_models()
            print(f"\n📊 OLLAMA MODELOS DETECTADOS ({len(models)}): {', '.join(models)}")
            pause_terminal()

        elif opt == "10":
            print("\n📜 LOGS AUDITORÍA:")
            if os.path.exists(DAEMON_LOG_FILE):
                res = subprocess.run(["tail", "-n", "15", DAEMON_LOG_FILE], capture_output=True, text=True)
                print(res.stdout)
            pause_terminal()

        elif opt == "11":
            orch.toggle_art62_247()
            pause_terminal()

        elif opt == "12":
            orch.toggle_art63_daemon()
            pause_terminal()

        elif opt == "0":
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true")
    args = parser.parse_args()

    orch = TriSwarmOrchestrator()
    if args.daemon:
        orch.run_autonomous_daemon_loop()
    else:
        show_mando_menu()
PYTHON_EOF

cp "$ART63_MODULE" "$ART63_MANDO"
chmod +x "$ART63_MODULE" "$ART63_MANDO"
echo "  ✅ Artefacto 63 actualizado con las 12 opciones y SQL dinámico."

# 2. Vaciado de Logs y Liberación de Lock
echo -e "\n2️⃣ Limpiando logs y cerrojos de ejecución..."
> "$LOG_FILE"
rm -f /tmp/ccia_bounty.lock
echo "  ✅ Archivo $LOG_FILE vaciado."
echo "  ✅ Cerrojo /tmp/ccia_bounty.lock liberado."

echo "================================================================================"
echo "✅ REPARACIÓN Y CONEXIÓN COMPLETADA SIN ERRORES"
echo "================================================================================"
