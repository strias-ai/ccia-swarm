import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"
MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ RESTAURANDO CCIA_MISSION_CONTROL.PY Y ENLAZANDO CCIA_MANDO_63.PY")
print("=" * 80)

if os.path.exists(MANDO_PATH):
    print(f"  ✅ CONFIRMADO: El Centro de Mando ({MANDO_PATH}) está INTACTO.")
else:
    print(f"  ❌ ALERTA: No se encuentra {MANDO_PATH}")

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Purgar todas las líneas de parcheo previo que causaban IndentationError
clean_lines = []
for line in lines:
    if any(k in line for k in ["ccia_mando_63", "str(art_id) == \"63\"", "str(art_id) == '63'"]):
        continue
    clean_lines.append(line)

clean_code = "".join(clean_lines)

# 2. Inyectar la asignación limpia de script_path dentro de artifact_sub_menu
pattern = r'(def artifact_sub_menu\(art_id\):[\s\S]*?)(script_path\s*=\s*os\.path\.join\([^\n]+\))'
replacement = r'''\1\2
    if str(art_id) == "63":
        script_path = "/home/k1/ccia_workspace/ccia_mando_63.py"'''

if re.search(pattern, clean_code):
    fixed_code = re.sub(pattern, replacement, clean_code, count=1)
else:
    fixed_code = clean_code

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.write(fixed_code)

# 3. Comprobar compilación de sintaxis
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py restaurado y compilado sin errores.")
except Exception as e:
    print(f"  ⚠️ Error de compilación residual: {e}")
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        err_lines = f.readlines()
    print("\n--- REVISIÓN DE LÍNEAS 75 A 95 ---")
    for i in range(max(0, 74), min(len(err_lines), 95)):
        print(f"{i+1:4d}: {err_lines[i].rstrip()}")

print("=" * 80)
