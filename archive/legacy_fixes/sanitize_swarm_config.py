import json
import os
import subprocess

cfg_path = "/home/k1/ccia_workspace/swarm_config.json"

# 1. Obtener lista actual de modelos instalados en Ollama
try:
    res = subprocess.check_output(["ollama", "list"], stderr=subprocess.DEVNULL).decode("utf-8")
    lines = res.strip().splitlines()[1:]
    available_models = [line.split()[0] for line in lines if line.strip()]
except Exception:
    available_models = [
        "richardyoung/qwen2.5-7b-instruct-abliterated:latest",
        "ccia-reina-r1coder-14b:latest",
        "huihui_ai/deepseek-r1-abliterated:7b",
        "ccia-coder-xl-14b:latest"
    ]

# 2. Corregir entradas numéricas literales en swarm_config.json
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for item in data.get("brains", []) + data.get("queen_brains", []):
        m = item.get("model", "").strip()
        if m.isdigit():
            idx = int(m) - 1
            if 0 <= idx < len(available_models):
                item["model"] = available_models[idx]
                changed = True

    if changed:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("✅ Se corrigieron exitosamente las entradas numéricas por sus nombres de modelo reales.\n")

    # 3. Mostrar auditoría final del archivo en disco
    with open(cfg_path, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    print("📋 ESTADO REAL EN DISCO (swarm_config.json):")
    print("─" * 70)
    for b in final_data.get("brains", []):
        print(f"  • Enjambre {b.get('swarm')}: [Cerebro {b['code']}] {b['role']} --> {b['model']}")
    print("─" * 70)
    for q in final_data.get("queen_brains", []):
        print(f"  👑 [REINA {q['code']}] {q['role']} --> {q['model']}")
    print("─" * 70)

