import py_compile

mando_menu_code = r"""def show_mando_menu():
    orch = TriSwarmOrchestrator()

    while True:
        try:
            conn = sqlite3.connect(orch.db_path)
            cur = conn.cursor()
            cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
            row = cur.fetchone()
            conn.close()
            status_62 = row[0] if row else "DISABLED"
        except Exception:
            status_62 = "UNKNOWN"

        daemon_running, daemon_pid = orch.get_art63_daemon_status()
        status_daemon = f"🟢 ACTIVO (PID: {daemon_pid})" if daemon_running else "🔴 INACTIVO"
        has_lock = os.path.exists(LOCK_FILE)

        print("")
        print("================================================================================")
        print(" 🎛️  CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62")
        print("================================================================================")
        print(f" Estado Bucle 24/7 Artefacto 62 : [{status_62}]")
        print(f" Daemon Bucle 24/7 Artefacto 63 : [{status_daemon}]")
        print(f" Cerrojo Mutex (/tmp)          : [{'RECLAMADO' if has_lock else 'LIBRE'}]")
        print("--------------------------------------------------------------------------------")
        print("  [1] 📋 Ver Mapeo Actual y Estado del Enjambre")
        print("  [2] 🧠 Reconfigurar Modelos de Ollama para los 15 Cerebros")
        print("  [3] 🚀 Lanzar Ejecución Completa Tri-Enjambre con Supervisión Reina")
        print("  [4] 🎯 Submenú de Control y Búsqueda de Bounties")
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
        print("================================================================================")

        opt = input("CCiA-Mando-63> ").strip()

        if opt == "1":
            print("\n📋 MAPEO ACTUAL DEL SWARM:")
            for b in orch.brains:
                print(f"  [{b['code']}] {b['icon']} CEREBRO {b['code']} ({b['role']:<24}) ──> {b['model']}")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "2":
            models = orch.list_ollama_models()
            print("\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA PARA LOS 15 CEREBROS:")
            for b in orch.brains:
                print(f"  [{b['code']}] {b['role']:<25} -> Actual: {b['model']}")
            print("\nModelos Ollama locales disponibles:")
            for idx, m in enumerate(models, 1):
                print(f"  [{idx}] {m}")
            
            b_code = input("\nSelecciona código de cerebro a reconfigurar (ej. 1.1 a 3.5): ").strip()
            b_match = [b for b in orch.brains if b["code"] == b_code]
            if b_match:
                m_num = input(f"Selecciona nº de modelo para Cerebro {b_code}: ").strip()
                if m_num.isdigit() and 1 <= int(m_num) <= len(models):
                    b_match[0]["model"] = models[int(m_num) - 1]
                    orch.save_brains()
                    print("✅ Modelo actualizado con éxito.")
            else:
                print("⚠️ Código de cerebro no encontrado.")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "3":
            orch.run_full_pipeline()
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "4":
            print("\n🎯 BÚSQUEDA Y SELECCIÓN DE BOUNTIES (GITHUB API)")
            term = input("Ingresa término de búsqueda (ej. 'python', 'fix' o Presiona ENTER para default 'bounty'): ").strip()
            cmd = ["gh", "search", "issues", term if term else "bounty", "--state", "open", "--limit", "10", "--json", "repository,number,title"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                try:
                    items = json.loads(res.stdout)
                    for idx, it in enumerate(items, 1):
                        repo = it.get("repository", {}).get("nameWithOwner")
                        num = it.get("number")
                        print(f"  [{idx}] {repo}#{num} ── {it.get('title')[:60]}")
                    sel = input("\nSelecciona nº para procesar inmediatamente con la Reina (o 0 para cancelar): ").strip()
                    if sel.isdigit() and 1 <= int(sel) <= len(items):
                        target = items[int(sel)-1]
                        orch.run_full_pipeline(target["repository"]["nameWithOwner"], str(target["number"]))
                except Exception as e:
                    print(f"⚠️ Error parseando salida: {e}")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "5":
            print("\n💳 CONFIGURACIÓN DE CARTERAS DE RECEPCIÓN (CCiA HUB)")
            print("  1. Lightning Address            : vellichorlate475846@getalby.com")
            print("  2. EVM (ETH/Base/Arb/OP/Polygon): 0x6040f4D8BA36214222d34E176634670407a9bC56")
            print("  3. BTC Address (Native SegWit)  : bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59")
            print("  4. Solana (USDC/SOL - Superteam): Configurar dirección SOL")
            print("  5. TON Network (Telegram Bots)  : Configurar dirección TON")
            print("  6. Sui Network (Move Bounties)  : Configurar dirección SUI")
            print("  7. NEAR Protocol (AI Agent Hub) : Configurar dirección NEAR")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "6":
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT id, repo, issue_id, status, created_at, swarm1_draft FROM bounty_swarm_history ORDER BY id DESC LIMIT 5;")
                rows = cur.fetchall()
                conn.close()
                print("\n🧠 ÚLTIMOS DEBATES REGISTRADOS (bounty_swarm_history):")
                for r in rows:
                    print(f" ID #{r[0]} | Repo: {r[1]}#{r[2]} | Estado: {r[3]} | Fecha: {r[4]}")
                    print(f" Output/Borrador:\n{str(r[5])[:300]}\n--------------------------------------------------")
            except Exception as e:
                print(f"⚠️ Error al consultar historial DB: {e}")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "7":
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT id, issue_key, solution_summary, created_at FROM bounty_vector_memory ORDER BY id DESC LIMIT 5;")
                rows = cur.fetchall()
                conn.close()
                print("\n📑 REVISIONES DE CALIDAD / MEMORIA VECTORIAL DE SOLUCIONES:")
                if not rows:
                    print("  (Sin registros en bounty_vector_memory aún)")
                for r in rows:
                    print(f" ID #{r[0]} | Issue: {r[1]} | Fecha: {r[3]}\n Resumen: {r[2]}\n--------------------------------------------------")
            except Exception as e:
                print(f"⚠️ Error al consultar memoria vectorial: {e}")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "8":
            print("\n📡 MONITOR DE RAZONAMIENTO EN TIEMPO REAL (LIVE OLLAMA STREAM)")
            print("Conectando al log autónomo... (Presiona Ctrl+C para salir al menú)")
            print("================================================================================")
            log_file = getattr(orch, "daemon_log_file", "/tmp/art63_daemon.log")
            if not os.path.exists(log_file):
                open(log_file, "a").close()
            try:
                proc = subprocess.Popen(["tail", "-n", "40", "-f", log_file])
                proc.wait()
            except KeyboardInterrupt:
                print("\n\n📡 Saliendo del Monitor en vivo...")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "9":
            print("\n📊 ESTADO DE TABLAS DB Y CONEXIÓN OLLAMA LOCAL")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cur.fetchall()]
                conn.close()
                print(f"  Tablas en DB ({orch.db_path}): {', '.join(tables)}")
            except Exception as e:
                print(f"  ⚠️ Error consultando DB: {e}")
            models = orch.list_ollama_models()
            print(f"  Modelos Ollama locales activos: {len(models)}")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "10":
            print("\n📜 LOGS EN VIVO & AUDITORÍA DE VERSIONES (Últimas 30 líneas):")
            log_file = getattr(orch, "daemon_log_file", "/tmp/art63_daemon.log")
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()[-30:]
                    print("".join(lines))
            else:
                print("  (El archivo de log autónomo no se ha creado aún)")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "11":
            orch.toggle_art62_247()
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "12":
            orch.toggle_art63_daemon()
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "13":
            if "show_queen_menu" in globals():
                show_queen_menu(orch)
            elif hasattr(orch, "show_queen_menu"):
                orch.show_queen_menu()
            else:
                print("⚠️ Gobernanza Reina no configurada en este entorno.")
            input("\n[ Presiona ENTER para continuar... ]")

        elif opt == "0":
            print("👋 Saliendo del Centro de Mando...")
            break
"""

def apply_repair(filepath):
    print(f"🛠️ Reconstruyendo {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    cut_idx = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("def show_mando_menu():"):
            cut_idx = idx
            break

    if cut_idx != -1:
        valid_head = "".join(lines[:cut_idx])
    else:
        valid_head = "".join(lines)

    footer = "\n\nif __name__ == '__main__':\n    parser = argparse.ArgumentParser()\n    parser.add_argument('--daemon', action='store_true')\n    args = parser.parse_args()\n\n    orch = TriSwarmOrchestrator()\n    if args.daemon:\n        orch.run_autonomous_daemon_loop()\n    else:\n        show_mando_menu()\n"

    final_code = valid_head.rstrip() + "\n\n" + mando_menu_code.strip() + footer

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_code)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} RECONSTRUIDO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

apply_repair("/home/k1/ccia_workspace/ccia_mando_63.py")
apply_repair("/home/k1/ccia_workspace/modules/art_63.py")
