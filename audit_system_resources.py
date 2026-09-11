import subprocess

print("================================================================================")
print("🔍 AUDITORÍA DE PROCESOS ACTIVOS Y RECURSOS (CCiA + OLLAMA + LINUX)")
print("================================================================================")

# 1. Modelos de Ollama activos en memoria RAM
print("\n🧠 [1] MODELOS DE OLLAMA CARGADOS EN RAM (ollama ps):")
try:
    res = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=10)
    out = res.stdout.strip()
    print(out if out else "  • No hay ningún modelo de Ollama retenido en memoria.")
except Exception as e:
    print(f"  ⚠️ Error al consultar ollama ps: {e}")

# 2. Procesos CCiA y Python activos
print("\n🐍 [2] PROCESOS DE PYTHON / CCiA EN EJECUCIÓN:")
try:
    res = subprocess.run(["ps", "-eo", "pid,pcpu,pmem,args"], capture_output=True, text=True)
    lines = res.stdout.splitlines()
    header = lines[0]
    python_procs = [l for l in lines[1:] if "python" in l and "audit_system_resources" not in l and "grep" not in l]
    print(f"  {header}")
    if python_procs:
        for p in python_procs:
            print(f"  {p}")
    else:
        print("  • No hay otros scripts de Python corriendo en segundo plano.")
except Exception as e:
    print(f"  ⚠️ Error al consultar procesos Python: {e}")

# 3. Top 5 consumo CPU
print("\n⚡ [3] TOP 5 PROCESOS POR USO DE CPU:")
try:
    res = subprocess.run(["ps", "-eo", "pid,user,pcpu,pmem,comm", "--sort=-%cpu"], capture_output=True, text=True)
    lines = res.stdout.splitlines()[:6]
    for l in lines:
        print(f"  {l}")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# 4. Top 5 consumo RAM
print("\n💾 [4] TOP 5 PROCESOS POR USO DE MEMORIA RAM:")
try:
    res = subprocess.run(["ps", "-eo", "pid,user,pcpu,pmem,comm", "--sort=-%mem"], capture_output=True, text=True)
    lines = res.stdout.splitlines()[:6]
    for l in lines:
        print(f"  {l}")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

print("================================================================================")
