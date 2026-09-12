import os
import re
import json

print("=" * 80)
print("🛠️ PARCHEANDO PERSISTENCIA Y SELECCIÓN DE MODELOS PARA EL ENJAMBRE")
print("=" * 80)

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
cfg_path = "/home/k1/ccia_workspace/swarm_config.json"

# 1. Asegurar que swarm_config.json tenga la estructura base válida
default_config = {
    "brains": [
        {"code": "1.1", "swarm": 1, "role": "Archi-Investigador", "model": "ccia-reina-r1coder-14b:latest"},
        {"code": "1.2", "swarm": 1, "role": "Archi-Diseñador", "model": "ccia-reina-r1coder-14b:latest"},
        {"code": "1.3", "swarm": 1, "role": "Desarrollador Core", "model": "ccia-coder-xl-14b:latest"},
        {"code": "1.4", "swarm": 1, "role": "Auditor Seguridad", "model": "ccia-coder-xl-14b:latest"},
        {"code": "1.5", "swarm": 1, "role": "Redactor Docs", "model": "dolphin-llama3:8b"},
        {"code": "2.1", "swarm": 2, "role": "Frontend Specialist", "model": "ccia-coder-xl-14b:latest"},
        {"code": "2.2", "swarm": 2, "role": "Backend Smart Contracts", "model": "ccia-coder-xl-14b:latest"},
        {"code": "2.3", "swarm": 2, "role": "QA & Testing", "model": "ccia-coder-xl-14b:latest"},
        {"code": "2.4", "swarm": 2, "role": "DevOps & CI/CD", "model": "mistral-nemo:12b"},
        {"code": "2.5", "swarm": 2, "role": "UX/Technical Writer", "model": "ccia-coder-xl-14b:latest"},
        {"code": "3.1", "swarm": 3, "role": "Validator Web3/DeFi", "model": "ccia-coder-xl-14b:latest"},
        {"code": "3.2", "swarm": 3, "role": "Cryptographic Auditor", "model": "ccia-reina-r1coder-14b:latest"},
        {"code": "3.3", "swarm": 3, "role": "PR & Community Lead", "model": "ccia-coder-xl-14b:latest"},
        {"code": "3.4", "swarm": 3, "role": "Tokenomics Expert", "model": "ccia-coder-xl-14b:latest"},
        {"code": "3.5", "swarm": 3, "role": "Legal & ProBono Compliance", "model": "ccia-reina-r1coder-14b:latest"}
    ],
    "queen_brains": [
        {"code": "Q1", "role": "Reina Gobernanza & Estrategia", "model": "ccia-reina-r1coder-14b:latest"},
        {"code": "Q2", "role": "Reina Calidad & Código", "model": "ccia-coder-xl-14b:latest"},
        {"code": "Q3", "role": "Reina Síntesis & Publicación", "model": "mistral-nemo:12b"}
    ]
}

if not os.path.exists(cfg_path):
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)
    print("✅ Creado archivo de configuración base: swarm_config.json")

# 2. Reemplazar la lógica de la Opción 2 en ccia_mando_63.py
if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        mando_code = f.read()

    new_opt2_logic = '''        elif opt == "2":
            print("\\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA:")
            print("Modelos instalados detectados:")
            models = orch.available_models
            for idx, m in enumerate(models, 1):
                print(f"  {idx}. {m}")
            
            print("\\nSeleccione Cerebro a reconfigurar (ejemplo: 1.1, 2.3, Q1, o 'TODOS'):")
            target = input("Código de Cerebro > ").strip()
            if target:
                print("\\nIndique el modelo deseado escribiendo su NÚMERO (1-{}) o el NOMBRE EXACTO:".format(len(models)))
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
                    print(f"\\n✅ Cerebro(s) [{target.upper()}] reconfigurado(s) exitosamente a: {selected_model}")
            input("\\n[Presione ENTER para continuar...]")'''

    # Reemplazar la sección de la Opción 2 mediante regex
    pattern = r'elif opt == "2":.*?(?=elif opt == "3":)'
    if re.search(pattern, mando_code, re.DOTALL):
        mando_code = re.sub(pattern, new_opt2_logic + "\n\n        ", mando_code, flags=re.DOTALL)
        with open(mando_path, "w", encoding="utf-8") as f:
            f.write(mando_code)
        print("✅ Lógica de Opción 2 parcheada con soporte para selección por número e índice.")

# 3. Forzar en modules/art_63.py la carga de swarm_config.json al iniciar y al ejecutar
if os.path.exists(art63_path):
    with open(art63_path, "r", encoding="utf-8") as f:
        art_code = f.read()

    # Inyectar auto-load de swarm_config.json en la inicialización si no existe
    if "def load_swarm_config" in art_code and "self.load_swarm_config()" not in art_code:
        art_code = art_code.replace("def __init__(self):", "def __init__(self):\n        self.load_swarm_config()")
        with open(art63_path, "w", encoding="utf-8") as f:
            f.write(art_code)
        print("✅ Método auto-load inyectado en modules/art_63.py")

print("=" * 80)
print("🚀 PARCHE FINALIZADO CON ÉXITO")
print("=" * 80)
