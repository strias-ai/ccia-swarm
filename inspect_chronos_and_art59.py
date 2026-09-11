print("================================================================================")
print("🔍 INSPECCIÓN DE PROGRAMACIÓN EN CHRONOS Y LÓGICA DE ART_59")
print("================================================================================")

# 1. Ver programación en chronos_scheduler.py
chronos_path = "/home/k1/ccia_workspace/modules/chronos_scheduler.py"
print("\n📅 [1] PROGRAMACIÓN DE ART_59 EN CHRONOS_SCHEDULER.PY:")
try:
    with open(chronos_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if "art_59" in line or "schedule" in line.lower() or "run_module" in line:
                print(f"  Línea {i:03d} | {line.rstrip()}")
except Exception as e:
    print(f"  ⚠️ Error leyendo chronos_scheduler.py: {e}")

# 2. Ver la lógica completa de art_59.py
art59_path = "/home/k1/ccia_workspace/modules/art_59.py"
print("\n📄 [2] LÓGICA PRINCIPAL DE ART_59.PY:")
try:
    with open(art59_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content)
except Exception as e:
    print(f"  ⚠️ Error leyendo art_59.py: {e}")

print("================================================================================")
