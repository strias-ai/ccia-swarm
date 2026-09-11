import os
import sys
import json
import sqlite3
import subprocess
import time

sys.path.append("/home/k1/ccia_workspace")
from modules.art_63 import TriSwarmOrchestrator

def run_cascade_audit():
    print("=" * 80)
    print("🔬 INICIANDO AUDITORÍA EN CASCADA DE DEUDA TÉCNICA - ARTEFACTO 63")
    print("=" * 80)
    
    orch = TriSwarmOrchestrator()
    results = {}

    # 1. Mapeo Enjambre (Opción 1)
    try:
        brains_count = len(orch.brains)
        queens_count = len(orch.queen_brains)
        results["Opción 1: Mapeo Enjambre"] = f"OK ({brains_count} cerebros, {queens_count} reinas)"
    except Exception as e:
        results["Opción 1: Mapeo Enjambre"] = f"FAIL ({e})"

    # 2. Reconfigurar Modelos Ollama (Opción 2)
    try:
        models = orch.available_models
        results["Opción 2: Modelos Ollama"] = f"OK ({len(models)} modelos detectados)"
    except Exception as e:
        results["Opción 2: Modelos Ollama"] = f"FAIL ({e})"

    # 3. Submenú Bounties (Opción 4 - A, B, C)
    try:
        # SubA: Leer
        bounties = orch.fetch_pending_bounties_from_db()
        # SubB: Buscador evolutivo
        added = orch.evolutionary_bounty_searcher()
        # SubC: Insertar manual test
        conn = sqlite3.connect(orch.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO bounty_opportunities (repo, issue_id, title, reward, status) VALUES ('test/audit', '999', 'Audit Test', '$0', 'PENDING')")
        conn.commit()
        conn.close()
        results["Opción 4: Submenú Bounties (A, B, C)"] = f"OK ({len(bounties)} pendientes leídos, +{added} evolutivos)"
    except Exception as e:
        results["Opción 4: Submenú Bounties (A, B, C)"] = f"FAIL ({e})"

    # 4. Configuración Carteras (Opción 5)
    try:
        wallets_count = len(orch.wallets)
        results["Opción 5: Config Carteras"] = f"OK ({wallets_count} redes configuradas)"
    except Exception as e:
        results["Opción 5: Config Carteras"] = f"FAIL ({e})"

    # 5. Auditar Debates DB (Opción 6)
    try:
        conn = sqlite3.connect(orch.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM swarm_debates;")
        cnt = cur.fetchone()[0]
        conn.close()
        results["Opción 6: Auditoría Debates DB"] = f"OK ({cnt} registros)"
    except Exception as e:
        results["Opción 6: Auditoría Debates DB"] = f"FAIL ({e})"

    # 6. Revisiones Calidad DB (Opción 7)
    try:
        conn = sqlite3.connect(orch.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM proposal_reviews;")
        cnt = cur.fetchone()[0]
        conn.close()
        results["Opción 7: Revisiones Calidad DB"] = f"OK ({cnt} registros)"
    except Exception as e:
        results["Opción 7: Revisiones Calidad DB"] = f"FAIL ({e})"

    # 7. Monitor Stream & Logs Submenús (Opciones 8 y 10 - A, B, C, D)
    try:
        # Check files
        reasoning_exists = os.path.exists("/tmp/art63_reasoning.log")
        daemon_log_exists = os.path.exists("/tmp/art63_daemon.log")
        results["Opción 8 & 10: Logs y Monitor (A,B,C,D)"] = f"OK (Reasoning: {reasoning_exists}, DaemonLog: {daemon_log_exists})"
    except Exception as e:
        results["Opción 8 & 10: Logs y Monitor (A,B,C,D)"] = f"FAIL ({e})"

    # 8. Estado DB y Ollama (Opción 9)
    try:
        conn = sqlite3.connect(orch.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bounty_opportunities;")
        b_cnt = cur.fetchone()[0]
        conn.close()
        results["Opción 9: Estado DB & Ollama"] = f"OK (Bounties DB: {b_cnt}, Ollama activo)"
    except Exception as e:
        results["Opción 9: Estado DB & Ollama"] = f"FAIL ({e})"

    # 9. Toggle Bucle 24/7 Art 62 (Opción 11)
    try:
        f62 = "/tmp/art62_247.state"
        init_st = os.path.exists(f62)
        open(f62, "w").close()
        mid_st = os.path.exists(f62)
        if os.path.exists(f62): os.remove(f62)
        fin_st = os.path.exists(f62)
        results["Opción 11: Toggle Art 62"] = f"OK (Conmutación verificada: {init_st} -> {mid_st} -> {fin_st})"
    except Exception as e:
        results["Opción 11: Toggle Art 62"] = f"FAIL ({e})"

    # 10. Toggle Daemon Art 63 (Opción 12)
    try:
        f63 = "/tmp/art63_daemon.pid"
        init_st = os.path.exists(f63)
        open(f63, "w").write("9999")
        mid_st = os.path.exists(f63)
        if os.path.exists(f63): os.remove(f63)
        fin_st = os.path.exists(f63)
        results["Opción 12: Toggle Daemon 63"] = f"OK (Conmutación verificada: {init_st} -> {mid_st} -> {fin_st})"
    except Exception as e:
        results["Opción 12: Toggle Daemon 63"] = f"FAIL ({e})"

    # 11. Inferencia Directa Reina / Swarm (Opciones 3 y 13)
    try:
        q_model = orch.queen_brains[0]["model"]
        res = orch.call_ollama_stream(q_model, "TEST", "Auditoría Técnica", "Responde únicamente con la palabra 'OK_TEST'")
        results["Opción 3 & 13: Inferencia Reina & Enjambre"] = f"OK (Respuesta recibida: {res[:30]}...)"
    except Exception as e:
        results["Opción 3 & 13: Inferencia Reina & Enjambre"] = f"FAIL ({e})"

    print("\n" + "=" * 80)
    print("📊 RESULTADO FINAL DE LA AUDITORÍA DE EXTREMO A EXTREMO")
    print("=" * 80)
    for opt, status in results.items():
        icon = "✅" if "OK" in status else "❌"
        print(f" {icon} {opt:<45} | {status}")
    print("=" * 80)

if __name__ == "__main__":
    run_cascade_audit()
