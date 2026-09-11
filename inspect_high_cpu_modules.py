import subprocess

print("================================================================================")
print("🔍 INSPECCIÓN DE SUBPROCESOS EN CHRONOS_SCHEDULER")
print("================================================================================")

# 1. Inspeccionar comandos exactos de los procesos Python con mayor consumo
res = subprocess.run(["ps", "-eo", "pid,pcpu,pmem,args"], capture_output=True, text=True)
lines = [l for l in res.stdout.splitlines() if "python" in l or "ollama" in l]

print("\n⚡ PROCESOS RELEVANTES EN EJECUCIÓN:")
for l in lines:
    if any(k in l for k in ["chronos", "stripe", "outreach", "art_", "ollama"]):
        print(f"  • {l.strip()}")

# 2. Revisar el contenido de chronos_scheduler.py
chronos_path = "/home/k1/ccia_workspace/modules/chronos_scheduler.py"
print("\n📄 CONTENIDO COMPLETO DE CHRONOS_SCHEDULER.PY:")
try:
    with open(chronos_path, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"  ⚠️ Error al leer: {e}")

print("================================================================================")
