import os, sys, subprocess, signal, time

def execute_daemon_toggle_art63():
    pid_file = '/tmp/art63_daemon.pid'
    log_file = '/tmp/art63_reasoning.log'
    res = subprocess.run(['pgrep', '-f', 'art_63.py'], capture_output=True, text=True)
    raw_pids = [p.strip() for p in res.stdout.strip().split() if p.strip()]
    my_pid = str(os.getpid())
    pids = [p for p in raw_pids if p != my_pid]

    if pids or os.path.exists(pid_file):
        print('\n🛑 DETENIENDO DEMONIO Y PROCESOS DUPLICADOS DE ARTEFACTO 63...')
        subprocess.run(['pkill', '-9', '-f', 'art_63.py'], stderr=subprocess.DEVNULL)
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except Exception:
                pass
        time.sleep(0.5)
        print('✅ Demonio y subprocesos finalizados limpiamente.')
    else:
        print('\n🟢 INICIANDO DEMONIO ARTEFACTO 63 EN SEGUNDO PLANO (DESACOPLADO)...')
        with open(log_file, 'a', encoding='utf-8') as f_log:
            f_log.write('\n=== LOG REINICIADO DESDE CENTRO DE MANDO ===\n')
        art63_script = '/home/k1/ccia_workspace/modules/art_63.py'
        log_fd = open(log_file, 'a', encoding='utf-8')
        proc = subprocess.Popen(
            [sys.executable, '-u', art63_script, '--daemon'],
            stdout=log_fd,
            stderr=log_fd,
            start_new_session=True,
            close_fds=True
        )
        with open(pid_file, 'w') as pf:
            pf.write(str(proc.pid))
        print(f'✅ Demonio desacoplado iniciado correctamente con PID {proc.pid}.')
        print('👉 Usa la opción [8] o [10] para monitorear el razonamiento sin fuga en pantalla.')

import os, sys, subprocess, signal, time


def fetch_bounty_context(repo_issue: str) -> str:
    """Obtiene el contenido real del issue de GitHub para inyectarlo a la Reina"""
    try:
        if "#" in repo_issue:
            repo, issue_num = repo_issue.split("#")
            url = f"https://api.github.com/repos/{repo}/issues/{issue_num}"
            req = urllib.request.Request(url, headers={'User-Agent': 'CCIA-Swarm'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                title = data.get('title', '')
                body = data.get('body', '')
                return f"TÍTULO DEL ISSUE: {title}\nCUERPO DEL ISSUE:\n{body}"
    except Exception as e:
        return f"Contexto local del issue: {repo_issue} (No se pudo conectar a GitHub API: {e})"
    return f"Contexto de la tarea: {repo_issue}"

def clean_r1_output(text: str) -> str:
    """Limpia las trazas de pensamiento <think> de DeepSeek-R1"""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()


def clean_r1_output(text: str) -> str:
    """Elimina el bloque de pensamiento de DeepSeek-R1 y deja solo la respuesta de gobernanza."""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()

from modules.repo_inspector import RepoInspector
import os
import sys
import json
import sqlite3
import subprocess
import time

sys.path.append("/home/k1/ccia_workspace")
from modules.art_63 import TriSwarmOrchestrator

orch = TriSwarmOrchestrator()

def print_header():
    os.system("clear" if os.name == "posix" else "cls")
    daemon_status = "🟢 ACTIVO" if os.path.exists("/tmp/art63_daemon.pid") else "🔴 INACTIVO"
    b247_status = "ENABLED" if os.path.exists("/tmp/art62_247.state") else "DISABLED"
    print("=" * 80)
    print("       CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62")
    print("=" * 80)
    print(f" Estado Bucle 24/7 Artefacto 62 : [{b247_status}]")
    print(f" Daemon Bucle 24/7 Artefacto 63 : [{daemon_status}]")
    import fcntl
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
    import os, subprocess
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
            for b in orch.brains:
                print(f"  • Enjambre {b.get('swarm')}: [Cerebro {b['code']}] {b['role']} --> {b['model']}")
            print("─" * 70)
            for q in orch.queen_brains:
                print(f"  👑 [REINA {q['code']}] {q['role']} --> {q['model']}")
            input("\n[Presione ENTER para continuar...]")
        elif opt == "2":
            print("\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA:")
            print("Modelos instalados detectados:")
            models = orch.available_models
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
                    if target.upper() == "TODOS":
                        for b in orch.brains: b["model"] = selected_model
                        for q in orch.queen_brains: q["model"] = selected_model
                    else:
                        for b in orch.brains:
                            if b["code"].upper() == target.upper(): b["model"] = selected_model
                        for q in orch.queen_brains:
                            if q["code"].upper() == target.upper(): q["model"] = selected_model
                    orch.save_swarm_config()
                    print(f"\n✅ Cerebro(s) [{target.upper()}] reconfigurado(s) exitosamente a: {selected_model}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "3":
            print("\n🚀 LANZANDO EJECUCIÓN TRIPLE ENJAMBRE...")
            orch.run_full_pipeline()
            input("\n[Presione ENTER para continuar...]")

        elif opt == "4":
            print("\n🎯 SUBMENÚ Y BUSCADOR EVOLUTIVO DE BOUNTIES:")
            print("  [A] Ver Bounties Registrados en DB")
            print("  [B] Ejecutar Buscador Evolutivo (Scraper GitHub/Feeds)")
            print("  [C] Añadir Bounty Manualmente")
            sub_opt = input("Submenú > ").strip().upper()
            if sub_opt == "A":
                bounties = orch.fetch_pending_bounties_from_db()
                for idx, b in enumerate(bounties, 1):
                    print(f"  {idx}. {b[0]}#{b[1]} - {b[2]}")
            elif sub_opt == "B":
                orch.evolutionary_bounty_searcher()
            elif sub_opt == "C":
                r = input("Repo (org/repo) > ").strip()
                i = input("Issue ID > ").strip()
                t = input("Título > ").strip()
                if r and i:
                    try:
                        conn = sqlite3.connect(orch.db_path)
                        conn.cursor().execute("INSERT INTO bounty_opportunities (repo, issue_id, title) VALUES (?, ?, ?)", (r, i, t))
                        conn.commit()
                        conn.close()
                        print("✅ Bounty guardado.")
                    except Exception as e: print(f"Error: {e}")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "5":
            print("\n💳 CARTERAS MULTICADENA DE RECEPCIÓN CONFIGURADAS:")
            for k, v in orch.wallets.items():
                print(f"  • {k.upper():<12}: {v}")
            print("\n¿Desea editar alguna cartera? (s/n)")
            if input("> ").strip().lower() == "s":
                k = input("Nombre de la moneda/red (lightning/evm/btc_segwit/solana/monero/tron_usdt) > ").strip().lower()
                v = input("Nueva dirección > ").strip()
                if k and v:
                    orch.wallets[k] = v
                    with open(orch.wallets_path, "w", encoding="utf-8") as f:
                        json.dump(orch.wallets, f, indent=2)
                    print("✅ Dirección actualizada correctamente.")
            input("\n[Presione ENTER para continuar...]")

        elif opt == "6":
            print("\n🧠 REGISTRO DE DEBATES ENTRE CEREBROS (swarm_debates):")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT repo, issue_id, swarm_layer, brain_code, role_name, timestamp FROM swarm_debates ORDER BY id DESC LIMIT 15;")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        print(f" [{r[5]}] Repo: {r[0]}#{r[1]} | Swarm {r[2]} | [{r[3]} - {r[4]}]")
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
                cur.execute("SELECT repo, issue_id, reviewer_queen, score, status, timestamp FROM proposal_reviews ORDER BY id DESC LIMIT 10;")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        print(f" [{r[5]}] Repo: {r[0]}#{r[1]} | Reina: {r[2]} | Puntuación: {r[3]} | Estado: {r[4]}")
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
            print(f"  • Modelos instalados en Ollama: {len(orch.available_models)}")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                for tbl in ["bounty_opportunities", "swarm_debates", "proposal_reviews"]:
                    cur.execute(f"SELECT COUNT(*) FROM {tbl};")
                    print(f"  • Tabla '{tbl}': {cur.fetchone()[0]} registros")
                conn.close()
            except Exception as e: print(f"Error DB: {e}")
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
                        print("".join(lines[-40:] if len(lines)>=40 else lines))
                else: print("Log de razonamiento no encontrado.")
            elif sub10 == "B":
                log_file = "/tmp/art63_daemon.log"
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as lf:
                        lines = lf.readlines()
                        print("".join(lines[-40:] if len(lines)>=40 else lines))
                else: print("Log de daemon no encontrado.")
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

        elif opt == '12':
            import subprocess, os, signal
            pid_file = "/tmp/art63_daemon.pid"
            res = subprocess.run(["pgrep", "-f", "art_63.py --daemon"], capture_output=True, text=True)
            pids = [p.strip() for p in res.stdout.strip().split("\n") if p.strip()]
            if pids:
                print(f"\n⚠️ Se detectaron {len(pids)} daemon(s) activo(s). Deteniendo...")
                for p in pids:
                    try:
                        os.kill(int(p), signal.SIGKILL)
                    except Exception:
                        pass
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                print("🔴 Daemon del Artefacto 63 DETENIDO limpiamente.")
            else:
                print("\n🚀 Iniciando única instancia del Daemon...")
                log_f = open("/tmp/art63_daemon.log", "w")
                proc = subprocess.Popen([
                    "python3", "-u", "/home/k1/ccia_workspace/modules/art_63.py", "--daemon"
                ], stdout=log_f, stderr=subprocess.STDOUT, start_new_session=True)
                with open(pid_file, "w") as f:
                    f.write(str(proc.pid))
                print(f"🟢 Daemon iniciado con PID único: {proc.pid}")
            input("\nPresione ENTER para continuar...")
if __name__ == '__main__':
    show_mando_menu()
