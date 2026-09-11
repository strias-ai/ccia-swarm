import os, glob

print("================================================================================")
print("🔍 AUDITORÍA STRUCTURAL Y BÚSQUEDA DE MENÚ DE MANDO")
print("================================================================================")

print("\n--- 1. Archivos Python en el workspace ---")
for f in sorted(glob.glob("/home/k1/ccia_workspace/**/*.py", recursive=True)):
    size = os.path.getsize(f)
    print(f"  • {f} ({size} bytes)")

targets = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for path in targets:
    if os.path.exists(path):
        print(f"\n--- 2. Estructura de funciones y menús en {os.path.basename(path)} ---")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"Total de líneas: {len(lines)}")
        for idx, line in enumerate(lines):
            s = line.strip()
            if any(s.startswith(p) for p in ["def ", "class ", "if opt", "elif opt", "while True"]) or any(k in s.lower() for k in ["cartera", "cerebro", "bounty", "opciones", " [1]", "[12]"]):
                print(f"  Línea {idx+1:4d} | {line.rstrip()[:90]}")

print("================================================================================")
