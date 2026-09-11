import os
import sys
import json
import subprocess

print("=" * 80)
print("🛠️ CORRIGIENDO MAPEO REAL DE MODELOS Y PERSISTENCIA DE CEREBROS")
print("=" * 80)

ws_dir = "/home/k1/ccia_workspace"
memory_dir = os.path.join(ws_dir, "swarm_memory")
os.makedirs(memory_dir, exist_ok=True)
config_json = os.path.join(memory_dir, "brain_models_config.json")

# Obtener modelos de Ollama activos
def get_ollama_models():
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split('\n')[1:]
        return [l.split()[0] for l in lines if l.strip()]
    except Exception:
        return []

models = get_ollama_models()
print(f"  • Modelos Ollama detectados ({len(models)}): {models[:3]}...")

# Tabla de fallbacks limpios
default_mapping = {
    "1.1": "huihui_ai/deepseek-r1-abliterated:14b",
    "1.2": "huihui_ai/deepseek-r1-abliterated:14b",
    "1.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "1.4": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "1.5": "dolphin-llama3:8b",
    "2.1": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.2": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.4": "mistral-nemo:12b",
    "2.5": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.1": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.2": "huihui_ai/deepseek-r1-abliterated:14b",
    "3.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.4": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.5": "huihui_ai/deepseek-r1-abliterated:14b",
    "Q1": "huihui_ai/deepseek-r1-abliterated:14b",
    "Q2": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "Q3": "mistral-nemo:12b"
}

# Sanitizar JSON de persistencia si tenía números guardados
cleaned_cfg = {}
if os.path.exists(config_json):
    try:
        with open(config_json, "r", encoding="utf-8") as f:
            raw_cfg = json.load(f)
        for k, v in raw_cfg.items():
            if str(v).isdigit():
                idx = int(v) - 1
                if 0 <= idx < len(models):
                    cleaned_cfg[k] = models[idx]
                else:
                    cleaned_cfg[k] = default_mapping.get(k, models[0] if models else "k1:latest")
            else:
                cleaned_cfg[k] = v
    except Exception:
        cleaned_cfg = default_mapping
else:
    cleaned_cfg = default_mapping

with open(config_json, "w", encoding="utf-8") as f:
    json.dump(cleaned_cfg, f, indent=2)

print("  ✅ Archivo swarm_memory/brain_models_config.json sanitizado y guardado con nombres reales.")

# Actualizar modules/art_63.py con la funciónget_brain_model
art63_path = os.path.join(ws_dir, "modules", "art_63.py")
with open(art63_path, "r", encoding="utf-8") as f:
    art63_code = f.read()

helper_function = '''
def get_brain_model(brain_id):
    cfg_p = "/home/k1/ccia_workspace/swarm_memory/brain_models_config.json"
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if brain_id in cfg and not str(cfg[brain_id]).isdigit():
                    return cfg[brain_id]
        except Exception:
            pass
    return "huihui_ai/qwen2.5-coder-abliterate:14b"
'''

if "def get_brain_model(" not in art63_code:
    art63_code = helper_function + "\n" + art63_code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(art63_code)
    print("  ✅ Función 'get_brain_model' inyectada en modules/art_63.py.")

subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Verificación de compilación completada.")
print("=" * 80)
