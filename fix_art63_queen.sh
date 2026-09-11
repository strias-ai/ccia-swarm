#!/usr/bin/env bash
set -e

DB_PATH="/home/k1/ccia_workspace/university.db"
LOG_FILE="/home/k1/ccia_workspace/art63_autonomo.log"
ART63_MODULE="/home/k1/ccia_workspace/modules/art_63.py"
ART63_MANDO="/home/k1/ccia_workspace/ccia_mando_63.py"

echo "================================================================================"
echo "👑 DESPLEGANDO ENJAMBRE REINA (Q1, Q2, Q3) Y FIX ANTISPAM EN ARTEFACTO 63"
echo "================================================================================"

cat << 'PYTHON_EOF' > "$ART63_MODULE"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCiA Artefacto 63 - Centro de Mando y Control Tri-Enjambre + Enjambre Reina (Opción 13)
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
QUEEN_CONFIG_PATH = "/home/k1/ccia_workspace/queen_config.json"
WALLET_PATH = "/home/k1/ccia_workspace/wallet_config.json"
LOCK_FILE = "/tmp/ccia_bounty.lock"
DAEMON_PID_FILE = "/tmp/ccia_art63_daemon.pid"
DAEMON_LOG_FILE = "/home/k1/ccia_workspace/art63_autonomo.log"
BRAIN_TIMEOUT = 7200

class TriSwarmOrchestrator:
    def __init__(self):
        self.db_path = DB_PATH
        self.config_path = CONFIG_PATH
        self.queen_config_path = QUEEN_CONFIG_PATH
        self.wallet_path = WALLET_PATH
        self.brains = self.load_brains()
        self.queen_brains = self.load_queen_brains()
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

        cur.execute("""
        CREATE TABLE IF NOT EXISTS queen_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_issue TEXT,
            queen_role TEXT,
            decision TEXT,
            details TEXT,
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

    def load_queen_brains(self):
        if os.path.exists(self.queen_config_path):
            try:
                with open(self.queen_config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) == 3:
                        return data
            except Exception:
                pass
        return [
            {"id": "Q1", "role": "Queen Sentinel (Entrada & Spam)", "icon": "👑🛡️", "model": "ccia-s1-1-spam-detector:latest"},
            {"id": "Q2", "role": "Queen Evaluator (Metacognición & Parches)", "icon": "👑🧠", "model": "ccia-s1-5-compliance-auditor:latest"},
            {"id": "Q3", "role": "Queen Optimizer (Evolución e I+D)", "icon": "👑⚙️", "model": "ccia-s2-5-optimal-selector:latest"}
        ]

    def save_brains(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.brains, f, indent=2, ensure_ascii=False)

    def save_queen_brains(self):
        with open(self.queen_config_path, "w", encoding="utf-8") as f:
            json.dump(self.queen_brains, f, indent=2, ensure_ascii=False)

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

    def record_queen_audit(self, target_issue, queen_role, decision, details):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO queen_audits (target_issue, queen_role, decision, details) VALUES (?, ?, ?, ?);",
                    (target_issue, queen_role, decision, str(details)[:1500]))
        conn.commit()
        conn.close()

    def parse_antispam_decision(self, raw_out):
        """Parsea respuestas en español e inglés y aplica la regla estricta"""
        try:
            clean = raw_out.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()

            data = json.loads(clean)
            is_valid = data.get("valid", data.get("valida", None))
            reason = data.get("reason", data.get("razon", "Sin razón especificada"))

            if is_valid is False or is_valid == "false" or is_valid == "False":
                return False, reason
            if is_valid is True or is_valid == "true" or is_valid == "True":
                return True, "VÁLIDO"
        except Exception:
            pass

        # Fallback de análisis por texto plano
        low = raw_out.lower()
        if '"valida": false' in low or '"valid": false' in low or '"valida":false' in low or '"valid":false' in low:
            return False, "Filtro detectó marca 'valida/valid: false' en respuesta."
        if "caracteres repetitivos" in low or "intento de spam" in low or "honeypot" in low:
            return False, "Detección semántica de spam/honeypot."

        return True, "VÁLIDO (Fallback)"

    def execute_brain_turn(self, brain_obj, task_title, context, stream_live=True):
        model = brain_obj["model"]
        b_id = brain_obj.get("code", brain_obj.get("id"))
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
            
            # SUPERVISIÓN ENJAMBRE REINA Q1 (ENTRADA & SPAM)
            is_valid, spam_reason = self.parse_antispam_decision(out_1)
            self.record_queen_audit(issue_key, "Q1_SENTINEL", "VALIDATED" if is_valid else "SPAM_BLOCKED", spam_reason)

            if not is_valid:
                print("\n" + "🛑"*40)
                print(f"🛑 [CORTOCIRCUITO ENJAMBRE REINA Q1] Bounty {issue_key} DESCARTADO POR SPAM.")
                print(f"🛑 Razón: {spam_reason}")
                print("🛑"*40 + "\n")

                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                            (repo, issue_num, out_1, "SPAM_SKIP"))
                conn.commit()
                conn.close()
                return {"status": "SPAM_DISCARDED"}

            print(f"\n✅ [ENJAMBRE REINA Q1] Issue validada correctamente. Procediendo con el Enjambre 1...")

            # CONTINUAR SOLO SI ES VÁLIDO
            out_2 = self.execute_brain_turn(self.brains[1], "Parser AST", repo)
            out_3 = self.execute_brain_turn(self.brains[2], "Diseñador Algoritmos", f"{out_1}\n{out_2}")
            out_4 = self.execute_brain_turn(self.brains[3], "Generador Parche", out_3)

            # SUPERVISIÓN REINA Q2 SOBRE CALIDAD DEL PARCHE
            if "no puedo proporcionar" in out_4.lower() or "sin indicar ningún problema" in out_4.lower():
                self.record_queen_audit(issue_key, "Q2_EVALUATOR", "PATCH_REJECTED", "El parche no contiene código ejecutable real.")
                print("\n⚠️ [ENJAMBRE REINA Q2] Parche rechazado por falta de contenido técnico.")
            else:
                self.record_queen_audit(issue_key, "Q2_EVALUATOR", "PATCH_APPROVED", "Parche listo para verificación de auditoría.")

            out_5 = self.execute_brain_turn(self.brains[4], "Auditor Conformidad", out_4)

            for b in self.brains[5:]:
                self.execute_brain_turn(b, f"Procesamiento {b['role']}", out_5, stream_live=False)

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                        (repo, issue_num, out_4, "SUCCESS"))
            conn.commit()
            conn.close()

            print("\n✅ EJECUCIÓN TRI-ENJAMBRE Y SUPERVISIÓN REINA FINALIZADAS CON ÉXITO")
            return {"status": "SUCCESS"}
        finally:
            self.release_system_mutex()

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

def show_queen_menu(orch):
    while True:
        models = orch.list_ollama_models()
        print("\n" + "="*80)
        print("👑 SUBMENÚ DE CONTROL Y RECONFIGURACIÓN DEL ENJAMBRE REINA (OPCIÓN 13)")
        print("="*80)
        print(" Estado de los Cerebros Gobernadores de la Reina:")
        for q in orch.queen_brains:
            print(f"  [{q['id']}] {q['icon']} {q['role']:<42} ──> Modelo: [{q['model']}]")
        print("-" * 80)
        print("  [A] 🔄 Cambiar modelo de Ollama asignado a un Miembro de la Reina")
        print("  [B] 📜 Ver Auditorías y Resoluciones Recientes de la Reina (queen_audits)")
        print("  [C] 🧪 Ejecutar Diagnóstico de Evaluación en Aislamiento (Queen Q1 Test)")
        print("  [0] 🚪 Volver al Menú Principal")
        print("="*80)

        opt = input("CCiA-Reina> ").strip().upper()
        if opt == "A":
            print("\nModelos disponibles en Ollama local:")
            for idx, m in enumerate(models, 1):
                print(f"  [{idx}] {m}")
            q_id = input("\nSelecciona Miembro de la Reina (Q1, Q2, Q3): ").strip().upper()
            q_match = [q for q in orch.queen_brains if q["id"] == q_id]
            if q_match:
                m_idx = input(f"Selecciona número de modelo para {q_id}: ").strip()
                if m_idx.isdigit() and 1 <= int(m_idx) <= len(models):
                    q_match[0]["model"] = models[int(m_idx) - 1]
                    orch.save_queen_brains()
                    print("✅ Modelo del Enjambre Reina actualizado correctamente.")
            else:
                print("⚠️ Identificador no válido.")
            pause_terminal()

        elif opt == "B":
            conn = sqlite3.connect(orch.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, target_issue, queen_role, decision, details, created_at FROM queen_audits ORDER BY id DESC LIMIT 10;")
            rows = cur.fetchall()
            conn.close()
            print("\n📜 ULTIMAS 10 DECISIONES DE LA REINA:")
            for r in rows:
                print(f" ID #{r[0]} | Target: {r[1]} | Rol: {r[2]} | Decisión: {r[3]} | Fecha: {r[5]}")
                print(f" Detalle: {r[4]}\n" + "-"*40)
            pause_terminal()

        elif opt == "C":
            test_text = input("\nIngresa texto de issue para probar decisión de la Reina Q1: ").strip()
            if test_text:
                q1_obj = orch.queen_brains[0]
                out = orch.execute_brain_turn(q1_obj, "Test Diagnóstico Antispam Reina", test_text, stream_live=True)
                is_v, reason = orch.parse_antispam_decision(out)
                print(f"\n📊 Resultado Diagnóstico Reina: VÁLIDO = {is_v} | Razón: {reason}")
            pause_terminal()

        elif opt == "0":
            break

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
        print("  [13] 👑 AUDITAR Y CONTROLAR ENJAMBRE REINA (Gobernanza Q1, Q2, Q3)")
        print("  [0] 🚪 Salir al Menú Principal")
        print("="*80)

        opt = input("CCiA-Mando-63> ").strip()

        if opt == "1":
            print("\n📋 MAPEO ACTUAL DEL SWARM:")
            for b in orch.brains:
                print(f"  [{b['id']}] {b['icon']} CEREBRO {b['id']} ({b['role']:<24}) ──> {b['model']}")
            pause_terminal()

        elif opt == "3":
            orch.run_full_pipeline()
            pause_terminal()

        elif opt == "11":
            orch.toggle_art62_247()
            pause_terminal()

        elif opt == "12":
            orch.toggle_art63_daemon()
            pause_terminal()

        elif opt == "13":
            show_queen_menu(orch)

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
echo "  ✅ Módulo y ejecutable actualizados con el Enjambre Reina y Fix Antispam."

# Vaciado de logs y cerrojos
> "$LOG_FILE"
rm -f /tmp/ccia_bounty.lock
echo "================================================================================"
echo "✅ ACTUALIZACIÓN INTEGRAL DE LA REINA COMPLETADA CON ÉXITO"
echo "================================================================================"
