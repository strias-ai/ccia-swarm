import os

files = [
    ("/home/k1/ccia_workspace/ccia_mando_63.py", 360, 565),
    ("/home/k1/ccia_workspace/modules/art_63.py", 440, 660)
]

for filepath, start, end in files:
    print(f"\n================================================================================")
    print(f"📄 INSPECCIONANDO MENÚ Y LÓGICA EN: {filepath}")
    print(f"================================================================================")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i in range(start - 1, min(end, len(lines))):
            print(f"{i+1:4d} | {lines[i]}", end="")

