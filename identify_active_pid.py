import subprocess

print("================================================================================")
print("🔍 IDENTIFICACIÓN DE SUBMÓDULO ACTIVO (PID)")
print("================================================================================")

# 1. Obtener detalles del proceso Python con mayor carga
res = subprocess.run(["ps", "-eo", "pid,ppid,pcpu,args"], capture_output=True, text=True)
lines = [l for l in res.stdout.splitlines() if "python" in l and "grep" not in l and "identify" not in l]

print("\n⚡ SUBPROCESOS PYTHON ACTUALES:")
for l in lines:
    print(f"  • {l.strip()}")

# 2. Buscar llamadas a Ollama dentro de los módulos ejecutados por Chronos
chronos_modules = [
    "/home/k1/ccia_workspace/modules/stripe_live_sync.py",
    "/home/k1/ccia_workspace/modules/autonomous_outreach_pipeline.py",
    "/home/k1/ccia_workspace/modules/sla_fulfillment_engine.py",
    "/home/k1/ccia_workspace/modules/treasury_vault_distributor.py",
    "/home/k1/ccia_workspace/modules/sentinel_tunnel_guard.py",
    "/home/k1/ccia_workspace/modules/a2a_market_gateway.py",
    "/home/k1/ccia_workspace/modules/art_61.py",
    "/home/k1/ccia_workspace/modules/art_60.py"
]

print("\n🔎 BÚSQUEDA DE CONSULTAS A OLLAMA EN MÓDULOS DE CHRONOS:")
for path in chronos_modules:
    res_grep = subprocess.run(["grep", "-rn", "ollama", path], capture_output=True, text=True)
    if res_grep.stdout:
        print(f"  • Módulo con Ollama: {path}")
        for line in res_grep.stdout.splitlines()[:3]:
            print(f"    └─ {line.strip()}")

print("================================================================================")
