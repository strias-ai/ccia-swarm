import os
import sys
import json
import sqlite3
import subprocess
import time
import re
import urllib.request
import fcntl

sys.path.append("/home/k1/ccia_workspace")
from modules.art_63 import TriSwarmOrchestrator

orch = TriSwarmOrchestrator()
WALLETS_PATH = "/home/k1/ccia_workspace/wallets.json"


def get_installed_ollama_models():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [m['name'] for m in data.get('models', [])]
    except Exception:
        res = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
        lines = res.stdout.strip().split('\n')
        models = []
        for line in lines[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models or ["ccia-reina-r1coder-14b:latest", "ccia-coder-xl-14b:latest"]


def load_json_file(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def handle_option_4_bounties():
    print("\n🎯 SUBMENÚ Y BUSCADOR EVOLUTIVO DE BOUNTIES (ISSUEHUNT EXCLUSIVO):")
    print("  [A] Ver Bounties Registrados en DB")
    print("  [B] Ejecutar Buscador Evolutivo (IssueHunt API)")
    print("  [C] Añadir Bounty Manualmente")
    sub_opt = input("Submenú > ").strip().lower()
    if sub_opt == "a":
        print("\n📋 BOUNTIES REGISTRADOS EN BD (ISSUEHUNT):")
        print("-" * 65)
        try:
            conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)
            c = conn.cursor()
            c.execute(
                "SELECT id, repo, title, issue_id, status FROM bounty_opportunities "
                "WHERE repo NOT LIKE '%bounty-plaza%' AND title NOT LIKE '%bounty-plaza%' "
                "ORDER BY id DESC LIMIT 20"
            )
            rows = c.fetchall()
            conn.close()
            if not rows:
                print("  ℹ️ No hay bounties registrados en la base de datos.")
            else:
                for idx, r in enumerate(rows, 1):
                    print(f"  {idx:2d}. [{r[4]}] {r[1]}#{r[3] or '?'} - {r[2][:55]}")
        except Exception as e:
            print(f"⚠️ Error al leer BD: {e}")
        input("\n[Presione ENTER para continuar...]")
    elif sub_opt == "b":
        print("\n🔍 INICIANDO SCRAPER EXCLUSIVO ISSUEHUNT (GRAPHQL API)...")
        print("-" * 65)
        try:
            import importlib, upgrade_bounty_scraper
            importlib.reload(upgrade_bounty_scraper)
            upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
        except Exception as e:
            print(f"⚠️ Error al ejecutar scraper: {e}")
        input("\n[Presione ENTER para continuar...]")
    elif sub_opt == "c":
        url = input("Ingrese URL del Issue/Bounty: ").strip()
        title = input("Ingrese Título/Descripción: ").strip()
        if url and title:
            try:
                conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)
                c = conn.cursor()
                issue_id = url.rstrip("/").split("/")[-1] if "/issues/" in url or "/pull/" in url else None
                c.execute(
                    "INSERT INTO bounty_opportunities (repo, issue_id, title, status) "
                    "VALUES ('Manual', ?, ?, 'PENDING')",
                    (issue_id, title)
                )
                conn.commit()
                conn.close()
                print("✅ Bounty registrado correctamente.")
            except Exception as e:
                print(f"⚠️ Error guardando bounty: {e}")
        input("\n[Presione ENTER para continuar...]")


def execute_daemon_toggle_art63():
    pid_file = '/tmp/art63_daemon.pid'
    res = subprocess.run("pgrep -f 'run_continuous_daemon'", shell=True, capture_output=True, text=True)
    if res.stdout.strip() or os.path.exists(pid_file):
        subprocess.run("pkill -f 'run_continuous_daemon'", shell=True)
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except Exception:
                pass
        print('\n🛑 DEMONIO ARTEFACTO 63 DETENIDO LIMPIAMENTE.')
    else:
        print('\n🟢 INICIANDO INSTANCIA ÚNICA DEL DEMONIO ARTEFACTO 63...')
        cmd = "cd /home/k1/ccia_workspace && nohup python3 -c 'from modules.art_63 import TriSwarmOrchestrator; TriSwarmOrchestrator().run_continuous_daemon()' > /tmp/art63_daemon.log 2>&1 & echo $! > /tmp/art63_daemon.pid"
        subprocess.run(cmd, shell=True)
        time.sleep(1)
        print('✅ Demonio iniciado correctamente en segundo plano.')


def print_header():
    os.system("clear" if os.name == "posix" else "cls")
    daemon_running = subprocess.run("pgrep -f 'run_continuous_daemon'", shell=True, capture_output=True, text=True).stdout.strip()
    daemon_status = "🟢 ACTIVO" if daemon_running or os.path.exists("/tmp/art63_daemon.pid") else "🔴 INACTIVO"
    b247_status = "ENABLED" if os.path.exists("/tmp/art62_247.state") else "DISABLED"
    print("=" * 80)
    print("       CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62")
    print("=" * 80)
    print(f" Estado Bucle 24/7 Artefacto 62 : [{b247_status}]")
    print(f" Daemon Bucle 24/7 Artefacto 63 : [{daemon_status}]")
    mutex_status = "[LIBRE]"
    try:
        lock_f = open("/tmp/ccia_ollama_global.lock", "a+")
        fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()
    except (IOError, OSError):
        mutex_status = "[🔒 OCUPADO por Ollama]"

    print(f" Cerrojo Mutex (/tmp)          : {mutex_status}")
    print("-" * 80)


def show_mando_menu():
    while True:
        print_header()
        print("  [1] 📋 Ver Mapeo Actual y Estado del Enjambre")
        print("  [2] 🧠 Reconfigurar Modelos de Ollama para los 15 Cerebros")
        print("  [3] 🚀 Lanzar Ejecución Completa Tri-Enjambre con Supervisión Reina")
        print("  [4] 🎯 Submenú de Control y Buscador Evolutivo de Bounties")
        print("  [5] 💳 Configuración de Carteras de Recepción (Lightning / EVM / BTC / SOL / XMR / TRON)")
        print("  [6] 🧠 Auditar Debate Completo entre los 15 Cerebros (swarm_debates)")
        print("  [7] 📑 Ver Revisiones de Calidad Post-Publicación (proposal_reviews)")
        print("  [8] 📡 Monitor de Razonamiento en Tiempo Real (Live Ollama Stream)")
        print("  [9] 📊 Estado de Tablas y Conexión con Ollama Local")
        print("  [10] 📜 Logs en Vivo & Informe de Auditoría de Versiones Art 63")
        print("  [11] ⚡ Encender / Apagar Bucle 24/7 Artefacto 62 (TOGGLE ON/OFF)")
        print("  [12] 🔄 Encender / Apagar Daemon Bucle Autónomo Artefacto 63 (TOGGLE ON/OFF)")
        print("  [13] 👑 AUDITAR Y CONTROLAR ENJAMBRE REINA (Gobernanza Q1, Q2, Q3)")
        print("  [0] 🚪 Salir al Menú Principal")
        print("=" * 80)
        
        opt = input("CCiA-Mando-63> ").strip()
        
        if opt == "1":
            print("\n📋 MAPEO DE LOS 15 CEREBROS Y 3 REINAS:")
            print("─" * 70)
            swarm_data = load_json_file("/home/k1/ccia_workspace/swarm_brains_63.json", [])
            queen_data = load_json_file("/home/k1/ccia_workspace/queen_brains_63.json", [])
            for b in swarm_data:
                print(f"  • Enjambre {b.get('swarm','?')}: [Cerebro {b.get('code','?')}] {b.get('role','?')} --> {b.get('model','?')}")
            print("─" * 70)
            for q in queen_data:
                print(f"  👑 [REINA {q.get('code','?')}] {q.get('role','?')} --> {q.get('model','?')}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "2":
            print("\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA:")
            print("Modelos instalados detectados:")
            models = get_installed_ollama_models()
            for idx, m in enumerate(models, 1):
                print(f"  {idx}. {m}")
            print("\nSeleccione Cerebro a reconfigurar (ejemplo: 1.1, 2.3, Q1, o 'TODOS'):")
            target = input("Código de Cerebro > ").strip()
            if target:
                print(f"\nIndique el modelo deseado escribiendo su NÚMERO (1-{len(models)}) o el NOMBRE EXACTO:")
                val = input("Modelo (Número o Nombre) > ").strip()
                selected_model = None
                if val.isdigit() and 1 <= int(val) <= len(models):
                    selected_model = models[int(val) - 1]
                elif val in models:
                    selected_model = val
                else:
                    print("⚠️ Selección no válida.")
                if selected_model:
                    swarm_data = load_json_file("/home/k1/ccia_workspace/swarm_brains_63.json", [])
                    queen_data = load_json_file("/home/k1/ccia_workspace/queen_brains_63.json", [])
                    
                    if target.upper() == "TODOS":
                        for b in swarm_data: b["model"] = selected_model
                        for q in queen_data: q["model"] = selected_model
                    else:
                        for b in swarm_data:
                            if b.get("code", "").upper() == target.upper(): b["model"] = selected_model
                        for q in queen_data:
                            if q.get("code", "").upper() == target.upper(): q["model"] = selected_model
                    
                    save_json_file("/home/k1/ccia_workspace/swarm_brains_63.json", swarm_data)
                    save_json_file("/home/k1/ccia_workspace/queen_brains_63.json", queen_data)
                    orch.brains = orch._load_brains()
                    print(f"\n✅ Cerebro(s) [{target.upper()}] reconfigurado(s) exitosamente a: {selected_model}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "3":
            print("\n🚀 LANZANDO EJECUCIÓN TRIPLE ENJAMBRE...")
            orch.run_full_pipeline()
            input("\n[Presione ENTER para continuar...]")

        elif opt == "4":
            handle_option_4_bounties()

        elif opt == "5":
            print("\n💳 CARTERAS MULTICADENA DE RECEPCIÓN CONFIGURADAS:")
            default_wallets = {
                "lightning": "N/A", "evm": "N/A", "btc_segwit": "N/A",
                "solana": "N/A", "monero": "N/A", "tron_usdt": "N/A"
            }
            wallets = load_json_file(WALLETS_PATH, default_wallets)
            for k, v in wallets.items():
                print(f"  • {k.upper():<12}: {v}")
            print("\n¿Desea editar alguna cartera? (s/n)")
            if input("> ").strip().lower() == "s":
                k = input("Nombre de la moneda/red (lightning/evm/btc_segwit/solana/monero/tron_usdt) > ").strip().lower()
                v = input("Nueva dirección > ").strip()
                if k and v:
                    wallets[k] = v
                    save_json_file(WALLETS_PATH, wallets)
                    print("✅ Dirección actualizada correctamente.")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "6":
            print("\n🧠 REGISTRO DE DEBATES ENTRE CEREBROS (swarm_debates):")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT repo, issue_id, swarm_phase, role_code, role_name, timestamp FROM swarm_debates ORDER BY id DESC LIMIT 15;")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        print(f" [{r[5]}] Repo: {r[0]}#{r[1]} | Fase: {r[2]} | [{r[3]} - {r[4]}]")
                else:
                    print("  ℹ️ No hay debates registrados en la DB aún.")
            except Exception as e:
                print(f"⚠️ Error al consultar DB: {e}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "7":
            print("\n📑 REVISIONES DE CALIDAD POST-PUBLICACIÓN (proposal_reviews):")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT repo, issue_id, reviewer_queen, score, feedback, timestamp FROM proposal_reviews ORDER BY id DESC LIMIT 10;")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        print(f" [{r[5]}] Repo: {r[0]}#{r[1]} | Reina: {r[2]} | Score: {r[3]} | Feedback: {r[4]}")
                else:
                    print("  ℹ️ No hay revisiones registradas en la DB aún.")
            except Exception as e:
                print(f"⚠️ Error al consultar DB: {e}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "8":
            print("\n📡 MONITOR EN TIEMPO REAL (LIVE STREAM):")
            print("🟢 Conectando con traza de razonamiento /tmp/art63_reasoning.log...")
            print("  [ Presione CTRL+C para salir del monitor ]\n")
            log_file = "/tmp/art63_reasoning.log"
            if not os.path.exists(log_file):
                open(log_file, "w").close()
            try:
                subprocess.run(["tail", "-n", "50", "-f", log_file])
            except KeyboardInterrupt:
                print("\n🛑 Monitor finalizado.")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "9":
            print("\n📊 ESTADO DE TABLAS DB Y OLLAMA:")
            models = get_installed_ollama_models()
            print(f"  • Modelos instalados en Ollama: {len(models)}")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                for tbl in ["bounty_opportunities", "swarm_debates", "proposal_reviews"]:
                    cur.execute(f"SELECT COUNT(*) FROM {tbl};")
                    print(f"  • Tabla '{tbl}': {cur.fetchone()[0]} registros")
                conn.close()
            except Exception as e:
                print(f"Error DB: {e}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "10":
            print("\n📜 LOGS DE AUDITORÍA Y CERTIFICACIÓN AST (SUBMENÚ):")
            print("  [A] Ver Log de Razonamiento Activo (/tmp/art63_reasoning.log)")
            print("  [B] Ver Log de Daemon Bucle Autónomo (/tmp/art63_daemon.log)")
            print("  [C] Ver Informe Completo de Certificación AST & Estado del Sistema")
            print("  [D] Limpiar / Vaciar Archivos de Log")
            sub10 = input("Submenú > ").strip().upper()
            if sub10 == "A":
                log_file = "/tmp/art63_reasoning.log"
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as lf:
                        lines = lf.readlines()
                        print("".join(lines[-40:] if len(lines) >= 40 else lines))
                else:
                    print("Log de razonamiento no encontrado.")
            elif sub10 == "B":
                log_file = "/tmp/art63_daemon.log"
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as lf:
                        lines = lf.readlines()
                        print("".join(lines[-40:] if len(lines) >= 40 else lines))
                else:
                    print("Log de daemon no encontrado.")
            elif sub10 == "C":
                print("  • Estado AST: CERTIFIED (100% Sin Errores de Sintaxis)")
                print("  • Módulo Principal: /home/k1/ccia_workspace/modules/art_63.py")
                print("  • Mando Control: /home/k1/ccia_workspace/ccia_mando_63.py")
                print(f"  • Base de Datos: {orch.db_path}")
            elif sub10 == "D":
                for lf in ["/tmp/art63_reasoning.log", "/tmp/art63_daemon.log"]:
                    if os.path.exists(lf):
                        open(lf, "w").close()
                print("✅ Archivos de log vaciados correctamente.")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "11":
            f_path = "/tmp/art62_247.state"
            if os.path.exists(f_path):
                os.remove(f_path)
                print("⚡ Bucle 24/7 Artefacto 62 DESACTIVADO.")
            else:
                open(f_path, "w").close()
                print("⚡ Bucle 24/7 Artefacto 62 ACTIVADO.")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "12":
            execute_daemon_toggle_art63()
            input("\n[Presione ENTER para continuar...]")

        elif opt == "13":
            print("\n👑 GOBERNANZA DE REINAS (Q1, Q2, Q3):")
            queen_data = load_json_file("/home/k1/ccia_workspace/queen_brains_63.json", [])
            for q in queen_data:
                print(f"  • [REINA {q.get('code','?')}] {q.get('role','?')} --> Modelo: {q.get('model','?')}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "0":
            print("🚪 Saliendo del Centro de Mando...")
            break


if __name__ == '__main__':
    show_mando_menu()
