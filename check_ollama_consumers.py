import subprocess
import os
import re

print("================================================================================")
print("🔍 INSPECCIÓN DE SERVICIOS Y RASTREO DE MODELOS OLLAMA EN ESPACIO DE TRABAJO")
print("================================================================================")

# 1. Buscar referencias explícitas al modelo retenido en código Python
model_query = "qwen2.5-coder-abliterate"
workspace_dir = "/home/k1"

print(f"\n[1] Buscando referencias a '{model_query}' en archivos Python en {workspace_dir}...")
matches = []
for root, dirs, files in os.walk(workspace_dir):
    if any(p in root for p in [".git", "venv", ".cache", "node_modules", "/tmp"]):
        continue
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if model_query in content:
                        matches.append(filepath)
            except Exception:
                pass

if matches:
    print(f"  📌 {len(matches)} archivos encontrados que referencian este modelo:")
    for m in matches[:10]:
        print(f"     - {m}")
else:
    print("  ℹ️ No se encontraron referencias duras en archivos .py (posible selección dinámica vía Open WebUI).")

# 2. Verificar puertos y conexiones activas hacia Ollama (11434)
print("\n[2] Verificando conexiones de red activas al puerto 11434 (Ollama):")
try:
    res = subprocess.run(["ss", "-tupn"], capture_output=True, text=True)
    ollama_conns = [line for line in res.stdout.splitlines() if "11434" in line]
    if ollama_conns:
        for c in ollama_conns:
            print(f"  🔗 {c}")
    else:
        print("  ℹ️ No hay conexiones TCP persistentes abiertas en este momento hacia el puerto 11434.")
except Exception as e:
    print(f"  ⚠️ Error revisando sockets: {e}")

# 3. Muestra de procesos activos relevantes
print("\n[3] Daemons activos que interactúan con la infraestructura de IA:")
daemons = ["open_webui", "sentinel.py", "chronos_scheduler.py", "vant_autonomous_daemon.py", "main_api:app"]
res_ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
for line in res_ps.stdout.splitlines():
    if any(d in line for d in daemons):
        parts = line.split()
        pid, cpu, mem, cmd = parts[1], parts[2], parts[3], " ".join(parts[10:])
        print(f"  - PID {pid:<8} | CPU: {cpu:>5}% | MEM: {mem:>4}% | {cmd[:80]}")

