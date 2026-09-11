import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"

print("=" * 80)
print("🛠️ CORRIGIENDO SANGRÍA Y APLICANDO OVERRIDE LIMPIO EN CCIA_MISSION_CONTROL.PY")
print("=" * 80)

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Eliminar cualquier línea rota o mal indentada previa alrededor de la opción [4]
cleaned_lines = []
skip = False
for line in lines:
    if "if str(art_id) == \"63\":" in line or "ccia_mando_63.py" in line:
        continue
    cleaned_lines.append(line)

content = "".join(cleaned_lines)

# 2. Inyectar el bloque con la sangría exacta (8 espacios para el if, 12 para el cuerpo)
target = '        print(f"  [4] 🚀 Lanzar Mando y Control'

override_block = (
    '        if str(art_id) == "63":\n'
    '            script_path = "/home/k1/ccia_workspace/ccia_mando_63.py"\n'
    '        print(f"  [4] 🚀 Lanzar Mando y Control'
)

if target in content:
    content = content.replace(target, override_block, 1)
    print("  ✅ Bloque de override inyectado con sangría correcta (8/12 espacios).")
else:
    print("  ❌ No se encontró la línea objetivo en ccia_mission_control.py.")

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.write(content)

# 3. Validar sintaxis AST y compilar
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py corregido y verificado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
