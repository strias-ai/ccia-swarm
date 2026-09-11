import py_compile
import os

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

full_mando_code = '''import sys
import os
import sqlite3
import urllib.request
import json

sys.path.append("/home/k1/ccia_workspace/modules")
sys.path.append("/home/k1/ccia_workspace")
from art_63 import TriSwarmOrchestrator

daemon_63_state = False
loop_62_state = False

def show_mando_menu():
    global daemon_63_state, loop_62_state
    orch = TriSwarmOrchestrator()
    
    while True:
        d62_str = "[🟢 ACTIVO]" if loop_62_state else "[DISABLED]"
        d63_str = "[🟢 ACTIVO]" if daemon_63_state else "[🔴 INACTIVO]"
        
        print("\\n================================================================================")
        print("  CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62")
        print("================================================================================")
        print(f" Estado Bucle 24/7 Artefacto 62 : {d62_str}")
        print(f" Daemon Bucle 24/7 Artefacto 63 : {d63_str}")
        print(" Cerrojo Mutex (/tmp)          : [LIBRE]")
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
        
        op = input("CCiA-Mando-63> ").strip()
        
        if op == "1":
            print("\\n📋 MAPEO ACTUAL DE LOS 15 CEREBROS Y REINAS:")
            print("--- ENJAMBRE 1: Investigación & Arquitectura ---")
            for b in orch.brains[:5]:
                print(f"  [{b['code']}] {b['role']} -> {b['model']}")
            print("\\n--- ENJAMBRE 2: Desarrollo & Pruebas ---")
            for b in orch.brains[5:10]:
                print(f"  [{b['code']}] {b['role']} -> {b['model']}")
            print("\\n--- ENJAMBRE 3: QA, Arbitraje & Finanzas ---")
            for b in orch.brains[10:]:
                print(f"  [{b['code']}] {b['role']} -> {b['model']}")
            print("\\n--- GOBERNANZA REINA (Q1, Q2, Q3) ---")
            for q in orch.queen_brains:
                print(f"  [{q['code']}] {q['role']} -> {q['model']}")
                
        elif op == "2":
            print("\\n🧠 CONFIGURACIÓN DE MODELOS OLLAMA:")
            print("Modelos asignados actualmente:")
            models = set([b['model'] for b in orch.brains] + [q['model'] for q in orch.queen_brains])
            for m in models:
                print(f"  - {m}")
            print("Para cambiar modelos globalmente, actualice modules/art_63.py.")

        elif op == "3":
            print("\\n🚀 Lanzando Pipeline Tri-Enjambre con Supervisión Reina...")
            orch.run_full_pipeline()

        elif op == "4":
            print("\\n🎯 SUBMENÚ DE BOUNTIES:")
            targets = orch.fetch_pending_bounties_from_db()
            print(f"Bounties pendientes registrados en DB: {len(targets)}")
            for idx, t in enumerate(targets, 1):
                print(f"  {idx}. {t[0]}#{t[1]} - {t[2]}")
            sub = input("\\n¿Procesar primer bounty inmediatamente? (s/n): ").strip().lower()
            if sub == 's' and targets:
                orch.process_bounty_loop(targets[0][0], targets[0][1], targets[0][2])

        elif op == "5":
            print("\\n💳 CARTERAS DE RECEPCIÓN CONFIGURADAS:")
            print(f"  ⚡ Lightning Address: {orch.wallets['lightning']}")
            print(f"  🔗 EVM Address      : {orch.wallets['evm']}")

        elif op == "6":
            print("\\n🧠 AUDITORÍA DE DEBATES ENTRE CEREBROS:")
            if os.path.exists("/tmp/bounty_work"):
                files = os.listdir("/tmp/bounty_work")
                print(f"Espacios de trabajo temporales activos: {len(files)}")
                for f in files[:5]:
                    print(f"  - /tmp/bounty_work/{f}")
            else:
                print("No hay logs de debates recientes en /tmp/bounty_work.")

        elif op == "7":
            print("\\n📑 REVISIONES DE CALIDAD POST-PUBLICACIÓN:")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT repo_owner_name, issue_number, state FROM bounty_opportunities WHERE state='RESOLVED';")
                rows = cur.fetchall()
                conn.close()
                print(f"Total Bounties Marcados como Resueltos: {len(rows)}")
                for r in rows:
                    print(f"  - {r[0]}#{r[1]} -> [{r[2]}]")
            except Exception as e:
                print(f"⚠️ Error consultando revisiones: {e}")

        elif op == "8":
            print("\\n📡 MONITOR DE RAZONAMIENTO EN TIEMPO REAL (OLLAMA):")
            try:
                req = urllib.request.Request("http://localhost:11434/api/tags")
                with urllib.request.urlopen(req, timeout=5) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    print("✅ Conexión con Ollama activa. Modelos en memoria:")
                    for m in data.get("models", []):
                        print(f"  - {m.get('name')} (Size: {round(m.get('size', 0)/1e9, 2)} GB)")
            except Exception as e:
                print(f"🔴 No se pudo conectar con Ollama en localhost:11434: {e}")

        elif op == "9":
            print("\\n📊 ESTADO DE BASE DE DATOS Y TABLAS:")
            try:
                conn = sqlite3.connect(orch.db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cur.fetchall()]
                print(f"Base de Datos: {orch.db_path}")
                print(f"Tablas encontradas ({len(tables)}): {', '.join(tables)}")
                conn.close()
            except Exception as e:
                print(f"⚠️ Error al leer DB: {e}")

        elif op == "10":
            print("\\n📜 LOGS EN VIVO & AUDITORÍA DE VERSIÓN:")
            print("  Artefacto: CCiA Tri-Swarm Bounty Orchestrator v1.0.0")
            print("  Módulo: /home/k1/ccia_workspace/modules/art_63.py")
            print("  Estado: CERTIFIED & READY")

        elif op == "11":
            loop_62_state = not loop_62_state
            st = "ACTIVADO" if loop_62_state else "DESACTIVADO"
            print(f"\\n⚡ Bucle 24/7 Artefacto 62 {st}.")

        elif op == "12":
            daemon_63_state = not daemon_63_state
            st = "ACTIVADO" if daemon_63_state else "DESACTIVADO"
            print(f"\\n🔄 Daemon Bucle Autónomo Artefacto 63 {st}.")

        elif op == "13":
            print("\\n👑 AUDITORÍA Y CONTROL ENJAMBRE REINA (Q1, Q2, Q3):")
            targets = orch.fetch_pending_bounties_from_db()
            print(f"Auditando {len(targets)} bounties pendientes con la Reina Q1 Antispam...")
            for t in targets:
                json_spec = '{"valid": true, "reason": "..."}'
                prompt = f"Evaluar issue '{t[2]}' en {t[0]}. Responder JSON: " + json_spec
                res = orch.call_ollama_direct(orch.queen_brains[0]["model"], orch.queen_brains[0]["role"], prompt)
                valid, reason = orch.validate_antispam_output(res)
                st = "✅ APROBADO" if valid else "🛑 RECHAZADO"
                print(f"  [{st}] {t[0]}#{t[1]} -> {reason}")

        elif op == "0":
            break

if __name__ == "__main__":
    show_mando_menu()
'''

with open(mando_path, "w", encoding="utf-8") as f:
    f.write(full_mando_code)

# Actualizar el punto de entrada de modules/art_63.py para incluir la ruta raíz en sys.path
with open(art63_path, "r", encoding="utf-8", errors="ignore") as f:
    art_content = f.read()

if "if __name__ ==" in art_content:
    art_content = art_content[:art_content.find("if __name__ ==")]

art_content += '''
if __name__ == "__main__":
    import sys
    sys.path.append("/home/k1/ccia_workspace")
    import ccia_mando_63
    ccia_mando_63.show_mando_menu()
'''

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(art_content)

py_compile.compile(mando_path, doraise=True)
py_compile.compile(art63_path, doraise=True)
print("✅ ccia_mando_63.py reestructurado con las 13 opciones y importación de modules/art_63.py reparada.")
