import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"

print("=" * 80)
print("🛠️ APLICANDO OVERRIDE DE RUTA PARA ARTEFACTO 63 EN CCIA_MISSION_CONTROL.PY")
print("=" * 80)

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    code = f.read()

# Limpiar posibles parches previos para evitar duplicados
code = re.sub(r'\n\s*if str\(art_id\) == [\'"]63[\'"]:\s*\n\s*script_path = [^\n]+\n', '', code)

# Marcador exacto previo a mostrar las opciones del submenú
marker = 'print(f"  [4] 🚀 Lanzar Mando y Control'

override_block = 'if str(art_id) == "63":\n        script_path = "/home/k1/ccia_workspace/ccia_mando_63.py"\n    '

if marker in code:
    code = code.replace(marker, override_block + marker)
    print("  ✅ Override inyectado correctamente en artifact_sub_menu(art_id).")
else:
    print("  ❌ No se encontró el marcador esperado en artifact_sub_menu.")

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.write(code)

# Verificación de sintaxis AST
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py compilado y validado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
