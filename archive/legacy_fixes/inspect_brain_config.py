import os
import sys
import json

print("=" * 80)
print("🔍 AUDITORÍA DE CONFIGURACIÓN Y MAPEADO DE CEREBROS EN ARTEFACTO 63")
print("=" * 80)

# 1. Inspeccionar archivo de persistencia de configuración de cerebros
config_file = "/home/k1/ccia_workspace/swarm_memory/brain_models_config.json"
print(f"\n1. 📄 Comprobando archivo de persistencia ({config_file}):")

if os.path.exists(config_file):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        print("  ✅ Archivo encontrado. Valores actualmente guardados:")
        for brain_id, model_val in cfg.items():
            status = "⚠️ ES UN ÍNDICE/NÚMERO (INCORRECTO)" if str(model_val).isdigit() else "🟢 MODELO VÁLIDO"
            print(f"    • [{brain_id:<4}]: {model_val:<45} | Status: {status}")
    except Exception as e:
        print(f"  ❌ Error leyendo JSON: {e}")
else:
    print("  ⚠️ El archivo brain_models_config.json no existe aún (usa valores hardcodeados).")

# 2. Inspeccionar estado en memoria importando el módulo
print("\n2. 🧠 Comprobando resolución interna en modules/art_63.py:")
try:
    sys.path.append("/home/k1/ccia_workspace")
    from modules.art_63 import BRAIN_MODEL_MAP, get_brain_model
    
    print("\n  • Mapeo en variable global BRAIN_MODEL_MAP:")
    for k, v in list(BRAIN_MODEL_MAP.items())[:8]: # Mostrar los primeros 8
        print(f"    - Cerebro {k:<4} -> Guardado: '{v}' | Resuelto por Ollama -> '{get_brain_model(k)}'")
        
except Exception as e:
    print(f"  ❌ Error inspeccionando art_63.py: {e}")

print("\n" + "=" * 80)
