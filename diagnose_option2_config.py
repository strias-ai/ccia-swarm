import os
import re
import json

print("=" * 80)
print("🔍 DIAGNÓSTICO DE PERSISTENCIA Y CONFIGURACIÓN DE CEREBROS (OPCIÓN 2)")
print("=" * 80)

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

# 1. Inspeccionar el manejo de la Opción 2 en ccia_mando_63.py
if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        mando_content = f.read()

    print("\n--- 1. CÓDIGO DE LA OPCIÓN [2] EN ccia_mando_63.py ---")
    lines = mando_content.splitlines()
    opt2_lines = []
    capture = False
    for i, line in enumerate(lines):
        if "RECONFIGURACIÓN DE MODELOS OLLAMA" in line or "Código de Cerebro >" in line:
            start = max(0, i - 10)
            end = min(len(lines), i + 40)
            opt2_lines = lines[start:end]
            break

    if opt2_lines:
        print("\n".join(opt2_lines))
    else:
        print("⚠️ No se encontró la etiqueta de la Opción 2 en ccia_mando_63.py.")

# 2. Inspeccionar la definición de modelos en modules/art_63.py
if os.path.exists(art63_path):
    with open(art63_path, "r", encoding="utf-8") as f:
        art63_content = f.read()

    print("\n--- 2. CONFIGURACIÓN HARDCODED / LECTURA EN modules/art_63.py ---")
    matches = re.findall(r'(BRAIN_MODELS|brain_models|MODELS_MAP|SWARM_CONFIG)\s*=\s*\{[^}]+\}', art63_content, re.DOTALL)
    if matches:
        for m in matches[:2]:
            print(m[:600])
    else:
        print("🔍 Buscando variables de asignación de modelos en art_63.py:")
        for line in art63_content.splitlines():
            if any(k in line for k in ["1.1", "2.1", "3.1", "Q1", "Q2"]) and "=" in line and ("qwen" in line.lower() or "deepseek" in line.lower() or "llama" in line.lower()):
                print(f"  • {line.strip()}")

# 3. Comprobar existencia de archivos de persistencia JSON
print("\n--- 3. ARCHIVOS DE PERSISTENCIA EN DISCO ---")
config_files = [
    "/home/k1/ccia_workspace/brain_models.json",
    "/home/k1/ccia_workspace/swarm_memory/brain_config.json",
    "/home/k1/ccia_workspace/swarm_config.json"
]

for cfg in config_files:
    exists = os.path.exists(cfg)
    status = "✅ EXISTE" if exists else "❌ NO EXISTE"
    print(f"• {cfg}: {status}")
    if exists:
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"  Contenido ({len(data)} entradas): {json.dumps(data, indent=2)[:300]}...")
        except Exception as e:
            print(f"  Error al leer {cfg}: {e}")

print("=" * 80)
