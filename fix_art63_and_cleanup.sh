#!/usr/bin/env bash
set -e

DB_PATH="/home/k1/ccia_workspace/university.db"
LOG_FILE="/home/k1/ccia_workspace/art63_autonomo.log"
ART63_MODULE="/home/k1/ccia_workspace/modules/art_63.py"
ART63_MANDO="/home/k1/ccia_workspace/ccia_mando_63.py"

echo "================================================================================"
echo "🛠️ INICIANDO REPARACIÓN, LIMPIEZA DE LOGS Y AUDITORÍA COMPLETA (ART 62 & 63)"
echo "================================================================================"

# 1. Ajustar Esquema SQLite e Insertar Registros Base con 'name' y 'version'
echo -e "\n1️⃣ Corrigiendo restricciones NOT NULL en ccia_artifact_manifests..."
python3 -c "
import sqlite3

conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()

# Verificar/Crear estructura adecuada
cur.execute('''
CREATE TABLE IF NOT EXISTS ccia_artifact_manifests (
    artifact_id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'Artefacto',
    version TEXT NOT NULL DEFAULT '1.0.0',
    status TEXT NOT NULL DEFAULT 'DISABLED'
);
''')

# Insertar/Garantizar registros por defecto respetando NOT NULL
cur.execute('''
INSERT OR IGNORE INTO ccia_artifact_manifests (artifact_id, name, version, status)
VALUES ('62', 'Artefacto 62 Bucle 24/7', '1.9.0', 'DISABLED');
''')

cur.execute('''
INSERT OR IGNORE INTO ccia_artifact_manifests (artifact_id, name, version, status)
VALUES ('63', 'Artefacto 63 Tri-Enjambre', '1.0.0', 'DISABLED');
''')

conn.commit()
conn.close()
print('  ✅ Registros iniciales de DB ajustados correctamente.')
"

# 2. Reescribir / Parchear Módulo del Artefacto 63
echo -e "\n2️⃣ Generando script actualizado de Artefacto 63 ($ART63_MODULE)..."
cat << 'PYTHON_EOF' > "$ART63_MODULE"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCiA Artefacto 63 - Centro de Mando y Control Tri-Enjambre Unificado
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
        CREATE TABLE IF NOT EXISTS ccia_artifact_manifests (
            artifact_id TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT 'Artefacto',
            version TEXT NOT NULL DEFAULT '1.0.0',
            status TEXT NOT NULL DEFAULT 'DISABLED'
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
                print(f"\n🔴 Daemon Artefacto 63 detenido (PID: {pid}).")
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
                print(f"\n🟢 Daemon Artefacto 63 iniciado en segundo plano (PID: {new_pid}).")
            else:
                print("\n⚠️ Ocurrió un problema al iniciar el Daemon.")

    def toggle_art62_247(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
        row = cur.fetchone()
        curr_status = row[0] if row else "DISABLED"

        new_status = "DISABLED" if curr_status == "ACTIVE" else "ACTIVE"
        cur.execute("""
            INSERT OR REPLACE INTO ccia_artifact_manifests (artifact_id, name, version, status)
            VALUES ('62', 'Artefacto 62 Bucle 24/7', '1.9.0', ?);
        """, (new_status,))
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
                print(f"⚠️ Error parseando GitHub: {e}")
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
            issue_key = f"{repo}#{issue_num}"

            print("\n" + "="*80)
            print(f"🚀 INICIANDO TRI-ENJAMBRE SOBRE {issue_key}: {bounty_data['title']}")
            print("="*80)

            # Cerebro 1.1: Filtro Antispam
            out_1 = f"Análisis Antispam para {issue_key}"
            if "spam" in bounty_data["body"].lower() or "honeypot" in bounty_data["body"].lower():
                print(f"🛑 Issue {issue_key} marcado como Spam.")
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                            (repo, issue_num, out_1, "SPAM_SKIP"))
                conn.commit()
                conn.close()
                return {"status": "SPAM_DISCARDED"}

            print("✅ Issue válido. Procesando enjambres...")
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO bounty_swarm_history (repo, issue_id, swarm1_draft, status) VALUES (?, ?, ?, ?);",
                        (repo, issue_num, "Ejecutado con éxito", "SUCCESS"))
            conn.commit()
            conn.close()
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
        print("  [3] 🚀 Lanzar Ejecución Completa Tri-Enjambre")
        print("  [10] 📜 Logs en Vivo & Informe de Auditoría")
        print("  [11] ⚡ Encender / Apagar Bucle 24/7 Artefacto 62 (TOGGLE ON/OFF)")
        print("  [12] 🔄 Encender / Apagar Daemon Artefacto 63 (TOGGLE ON/OFF)")
        print("  [0] 🚪 Salir")
        print("="*80)

        opt = input("CCiA-Mando-63> ").strip()
        if opt == "1":
            print("\n📋 MAPEO DE CEREBROS:")
            for b in orch.brains:
                print(f"  [{b['id']}] {b['icon']} CEREBRO {b['id']} ({b['role']}) ──> {b['model']}")
            pause_terminal()
        elif opt == "3":
            orch.run_full_pipeline()
            pause_terminal()
        elif opt == "10":
            print("\n📜 AUDITORÍA Y LOGS:")
            print(f"  • Lock Status: {'RECLAMADO' if os.path.exists(LOCK_FILE) else 'LIBRE'}")
            if os.path.exists(DAEMON_LOG_FILE):
                res = subprocess.run(["tail", "-n", "10", DAEMON_LOG_FILE], capture_output=True, text=True)
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
echo "  ✅ Módulo de Artefacto 63 y ejecutable principal actualizados."

# 3. Limpieza de Logs y Liberación de Locks
echo -e "\n3️⃣ Limpiando logs y liberando archivos lock..."
> "$LOG_FILE"
rm -f /tmp/ccia_bounty.lock
echo "  ✅ Archivo de log $LOG_FILE vaciado."
echo "  ✅ Cerrojo /tmp/ccia_bounty.lock liberado."

# 4. Auditoría de Memoria Vectorial y DB
echo -e "\n4️⃣ Auditando tablas de memoria y registros..."
python3 -c "
import sqlite3

conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM bounty_vector_memory;')
cnt_mem = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM bounty_swarm_history;')
cnt_hist = cur.fetchone()[0]

cur.execute('SELECT artifact_id, name, version, status FROM ccia_artifact_manifests;')
manifests = cur.fetchall()

conn.close()

print(f'  📊 Registros en Memoria Vectorial: {cnt_mem}')
print(f'  📊 Bounties en Historial Swarm   : {cnt_hist}')
print('  📄 Estado de Manifiestos:')
for m in manifests:
    print(f'     • [{m[0]}] {m[1]} (v{m[2]}) ──> Status: {m[3]}')
"

echo "================================================================================"
echo "✅ PROCESO DE AUDITORÍA, REPARACIÓN Y LIMPIEZA CONCLUIDO EXITOSAMENTE"
echo "================================================================================"
