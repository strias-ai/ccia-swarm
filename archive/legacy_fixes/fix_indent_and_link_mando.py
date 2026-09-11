import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"
MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ CORRIGIENDO SANGRÍA DE LÍNEA 84 Y VINCULANDO CCIA_MANDO_63.PY")
print("=" * 80)

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Corregir la sangría de la línea 84 de 4 a 8 espacios
fixed_lines = []
for line in lines:
    # Si la línea tiene 4 espacios antes de print(f"  [4] 🚀...
    if line.startswith('    print(f"  [4] 🚀') or line.startswith("    print(f'  [4] 🚀"):
        fixed_lines.append("    " + line) # Convertir 4 espacios en 8 espacios
    else:
        fixed_lines.append(line)

content = "".join(fixed_lines)

# 2. Asegurar la inyección limpia del override para el Artefacto 63
if 'if str(art_id) == "63":' not in content:
    pattern = r'(def artifact_sub_menu\(art_id\):[\s\S]*?script_filename\s*=\s*[^\n]+\n)'
    replacement = r'\1    if str(art_id) == "63":\n        script_path = "/home/k1/ccia_workspace/ccia_mando_63.py"\n'
    content = re.sub(pattern, replacement, content, count=1)

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.write(content)

# 3. Validar sintaxis AST y compilar
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        src = f.read()
    ast.parse(src)
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py corregido y compilado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
