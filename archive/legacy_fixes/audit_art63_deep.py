import sqlite3
import urllib.request
import json
import subprocess

def run_audit():
    print("=" * 80)
    print("🔍 AUDITORÍA TÉCNICA PROFUNDA - ARTEFACTO 63 & OLLAMA ENGINE")
    print("=" * 80)

    # 1. Verificar modelos disponibles en Ollama
    print("\n[1] Verificando catálogo de modelos locales en Ollama...")
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            available_models = [m["name"] for m in data.get("models", [])]
            print(f"  ✅ {len(available_models)} modelos disponibles en local:")
            for m in available_models:
                print(f"     - {m}")
    except Exception as e:
        print(f"  🔴 Error conectando a Ollama: {e}")
        available_models = []

    # 2. Verificar correspondencia con los 15 cerebros
    target_models = [
        "ccia-reina-r1coder-14b:latest",
        "ccia-coder-xl-14b:latest",
        "codestral:latest",
        "deepscaler:latest",
        "mistral-nemo:12b",
        "qwen2.5-coder:14b"
    ]
    
    print("\n[2] Verificando mapeo de modelos para los 15 Cerebros:")
    for tm in target_models:
        status = "✅ DISPONIBLE" if any(tm in am or am in tm for am in available_models) else "⚠️ NO INSTALADO (Se usará fallback)"
        print(f"  - {tm:<45} -> {status}")

    # 3. Inspeccionar esquema de tablas en DB
    print("\n[3] Inspeccionando estructura SQL en university.db...")
    try:
        conn = sqlite3.connect("/home/k1/ccia_workspace/university.db")
        cur = conn.cursor()
        for tbl in ["bounty_opportunities", "bounty_targets", "bounties"]:
            cur.execute(f"PRAGMA table_info({tbl});")
            cols = [c[1] for c in cur.fetchall()]
            if cols:
                print(f"  - Tabla '{tbl}': columnas = {cols}")
        conn.close()
    except Exception as e:
        print(f"  ⚠️ Error DB: {e}")

run_audit()
