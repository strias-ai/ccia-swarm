import os
import re
import glob
import subprocess

WORKSPACE = "/home/k1/ccia_workspace"

print("================================================================================")
print("🔍 CCiA CTO AUDITOR: MAPEO DE MODELOS Y CONEXIONES EN EL SISTEMA")
print("================================================================================")

# 1. Inspección de Modelfiles existentes en Ollama
target_models = ["ccia-s1-1-spam-detector", "ccia-s1-4-patch-generator", "k1:latest", "k4-architect:latest"]

print("\n--- 1. MODELFILES ACTUALES EN OLLAMA ---")
for model in target_models:
    print(f"\n📋 Modelfile de [{model}]:")
    try:
        res = subprocess.run(["ollama", "show", model, "--modelfile"], capture_output=True, text=True)
        if res.returncode == 0:
            lines = res.stdout.strip().split("\n")
            # Mostrar solo líneas relevantes (FROM y SYSTEM)
            for line in lines:
                if line.startswith("FROM") or line.startswith("SYSTEM") or "PARAMETER" in line:
                    print(f"  │ {line[:100]}")
        else:
            print(f"  ⚠️ No se pudo obtener el Modelfile de {model}")
    except Exception as e:
        print(f"  ❌ Error consultando {model}: {e}")

# 2. Búsqueda de Modelfiles en el disco local
print("\n--- 2. ARCHIVOS MODELFILE EN EL WORKSPACE ---")
modelfiles = glob.glob(f"{WORKSPACE}/**/Modelfile*", recursive=True) + glob.glob(f"{WORKSPACE}/**/*.modelfile", recursive=True)
if modelfiles:
    for mf in modelfiles:
        print(f"  • {mf}")
else:
    print("  ℹ️ No se encontraron archivos de Modelfile físicos guardados en el workspace.")

# 3. Búsqueda de referencias duras a nombres de modelos en código Python
print("\n--- 3. REFERENCIAS A MODELOS EN CÓDIGO PYTHON (modules/*.py) ---")
py_files = glob.glob(f"{WORKSPACE}/**/*.py", recursive=True)

patterns = [
    r'ccia-s[0-9]-[0-9]-[a-z-]+',
    r'qwen2\.5-coder[:a-z0-9_.-]*',
    r'deepseek-r1[:a-z0-9_.-]*',
    r'k1:latest',
    r'k4-architect:latest'
]

file_matches = {}

for py_file in py_files:
    if "venv" in py_file or "__pycache__" in py_file:
        continue
    try:
        with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            found = []
            for p in patterns:
                matches = re.findall(p, content)
                if matches:
                    found.extend(matches)
            if found:
                file_matches[os.path.basename(py_file)] = list(set(found))
    except Exception:
        pass

for filename, matches in file_matches.items():
    print(f"  📄 {filename}:")
    for m in matches:
        print(f"      └─> {m}")

print("\n================================================================================")
print("✅ INSPECCIÓN COMPLETA. LISTO PARA PLANIFICAR RECONSTRUCCIÓN DE MODELFILES.")
print("================================================================================")
