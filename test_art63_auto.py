#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import sqlite3
import json

sys.path.append('/home/k1/ccia_workspace')
from modules.art_63 import TriSwarmOrchestrator

def run_tests():
    print("================================================================================")
    echo_title = "🧪 EJECUTANDO DIAGNÓSTICO AUTOMATIZADO COMPLETO (ARTEFACTO 63 v5.2)"
    print(echo_title)
    print("================================================================================")

    orch = TriSwarmOrchestrator()

    # 1. Comprobación de Cerebros
    print("\n1️⃣  [ESTADO DE CEREBROS Y MODELOS OLLAMA]")
    print(f"   • Cerebros Tri-Enjambre  : {len(orch.brains)}/15 cargados correctamente")
    print(f"   • Gobernadores Reina     : {len(orch.queen_brains)}/3 (Q1, Q2, Q3)")
    models = orch.list_ollama_models()
    print(f"   • Modelos Ollama Activos : {len(models)} detectados ({', '.join(models[:3])}...)")

    # 2. Comprobación de Base de Datos
    print("\n2️⃣  [ESTADO DE TABLAS EN UNIVERSITY.DB]")
    conn = sqlite3.connect(orch.db_path)
    cur = conn.cursor()
    tables = ['bounty_swarm_history', 'bounty_vector_memory', 'queen_audits', 'ccia_artifact_manifests']
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            count = cur.fetchone()[0]
            print(f"   • Tabla {t:<22}: {count} filas")
        except Exception as e:
            print(f"   • Tabla {t:<22}: ERROR ({e})")
    conn.close()

    # 3. Comprobación del Filtro Antispam Q1 sobre Issue #772
    print("\n3️⃣  [PRUEBA DE RECHAZO DE SPAM EN REINA Q1 (Issue #772)]")
    test_title = "bounty"
    test_body = "We should create 3287452938572834 new issues for bounties so that repositories are flooded with low-quality or irrelevant bounty-only tasks..."
    
    q1_obj = orch.queen_brains[0]
    prompt = (
        f"Title: {test_title}\nBody: {test_body}\n\n"
        "INSTRUCCIÓN OBLIGATORIA: Responde ÚNICAMENTE un JSON estricto con el formato:\n"
        '{"valid": true, "reason": "explicacion"}\n'
        "Marca valid: false si detectas spam, texto troll, números repetitivos o solicitudes absurdas."
    )

    out = orch.execute_brain_turn(q1_obj, "Prueba Diagnóstica Antispam", prompt, stream_live=True)
    is_valid, reason = orch.parse_antispam_decision(out)

    print(f"\n   📊 Decisión Parseada : VÁLIDO = {is_valid}")
    print(f"   📊 Razón Registrada : {reason}")

    if not is_valid:
        print("   ✅ RESULTADO: EL FILTRO ANTISPAM Q1 DETUVO CORRECTAMENTE EL SPAM #772")
    else:
        print("   ⚠️ RESULTADO: La Reina permitió pasar el mensaje (revisar respuesta del modelo).")

    # 4. Estado del Daemon
    print("\n4️⃣  [ESTADO DEL DAEMON AUTÓNOMO 24/7]")
    is_running, pid = orch.get_art63_daemon_status()
    print(f"   • Daemon status: {'🟢 ACTIVO (PID ' + str(pid) + ')' if is_running else '🔴 INACTIVO'}")

    print("\n================================================================================")
    print("✨ DIAGNÓSTICO FINALIZADO CORRECTAMENTE")
    print("================================================================================")

if __name__ == "__main__":
    run_tests()
