import subprocess
import os

print("================================================================================")
print("🔍 INSPECCIÓN DE MAIN_API (UVICORN) Y ARTEFACTO 60 (ART_60.PY)")
print("================================================================================")

# 1. Inspeccionar proceso uvicorn duplicado/activo
res = subprocess.run(["ps", "-eo", "pid,pcpu,pmem,etime,args"], capture_output=True, text=True)
uvicorn_procs = [l for l in res.stdout.splitlines() if "main_api" in l and "grep" not in l]

print("\n⚡ INSTANCIAS DE MAIN_API EN EJECUCIÓN:")
for p in uvicorn_procs:
    print(f"  • {p.strip()}")

# 2. Ver llamadas a Ollama en art_60.py
art60_path = "/home/k1/ccia_workspace/modules/art_60.py"
print(f"\n📄 [1] REVISIÓN DE CONSULTAS A OLLAMA EN {art60_path}:")
if os.path.exists(art60_path):
    with open(art60_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if any(k in line for k in ["query_ollama", "get_ollama_installed_models", "brain_redactor", "sys_prompt"]):
                print(f"  Línea {i:03d} | {line.rstrip()}")
else:
    print("  ❌ Archivo art_60.py no encontrado.")

# 3. Comprobar si main_api.py existe en la raíz de workspace
main_api_path = "/home/k1/ccia_workspace/main_api.py"
if not os.path.exists(main_api_path):
    main_api_path = "/home/k1/main_api.py"

print(f"\n📄 [2] UBICACIÓN DE MAIN_API.PY: {main_api_path}")
if os.path.exists(main_api_path):
    size = os.path.getsize(main_api_path)
    print(f"  📏 Tamaño: {size} bytes")
else:
    print("  ❌ Archivo main_api.py no encontrado en rutas estándar.")

print("================================================================================")
