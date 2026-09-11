import os
import subprocess

print("================================================================================")
print("🔍 INSPECCIÓN DETALLADA DE ARTEFACTO 59 (art_59.py)")
print("================================================================================")

art59_path = "/home/k1/ccia_workspace/modules/art_59.py"

# 1. Verificación de existencia y tamaño
if os.path.exists(art59_path):
    size = os.path.getsize(art59_path)
    print(f"📁 Archivo: {art59_path}")
    print(f"📏 Tamaño: {size} bytes")
    
    # 2. Encabezado, Docstring y Primeras 40 líneas
    print("\n📄 [1] ENCABEZADO Y PRIMERAS LÍNEAS DE CÓDIGO:")
    print("--------------------------------------------------------------------------------")
    with open(art59_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:45], 1):
            print(f"{i:02d} | {line.rstrip()}")
    print("--------------------------------------------------------------------------------")
else:
    print(f"❌ El archivo {art59_path} no existe en esa ruta.")

# 3. Estado actual del proceso en ejecución
print("\n⚡ [2] ESTADO DE PROCESOS ACTIVOS DE ART_59 EN LINUX:")
res = subprocess.run(["ps", "-eo", "pid,pcpu,pmem,etime,args"], capture_output=True, text=True)
procs = [l for l in res.stdout.splitlines() if "art_59" in l and "grep" not in l and "inspect" not in l]

if procs:
    for p in procs:
        print(f"  • Proceso en ejecución: {p}")
else:
    print("  • No hay procesos activos de art_59.py en este momento.")

# 4. Comprobar si es invocado por Chronos Scheduler o algún daemon
print("\n⚙️ [3] REFERENCIAS A ART_59 EN OTROS MÓDULOS DEL CCiA:")
res_grep = subprocess.run(["grep", "-rn", "art_59", "/home/k1/ccia_workspace/"], capture_output=True, text=True)
refs = [l for l in res_grep.stdout.splitlines() if "inspect_art59" not in l]
if refs:
    for r in refs[:10]:
        print(f"  • {r}")
else:
    print("  • No se encontraron referencias externas directas.")

print("================================================================================")
