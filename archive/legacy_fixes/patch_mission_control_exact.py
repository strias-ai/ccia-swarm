import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"

print("=" * 80)
print("🛠️ ACTUALIZANDO REGISTRO DE ARTEFACTO 63 EN CCIA_MISSION_CONTROL.PY")
print("=" * 80)

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Inspeccionar y reemplazar cualquier asignación o diccionario donde se defina la ruta del Artefacto 63
# Patrón típico: 63: { ... "script": "...art_63.py" ... } o similar
old_target = "/home/k1/ccia_workspace/modules/art_63.py"
new_target = "/home/k1/ccia_workspace/ccia_mando_63.py"

updated_code = code

if old_target in updated_code:
    updated_code = updated_code.replace(old_target, new_target)
    print("  ✅ Ruta absoluta 'modules/art_63.py' sustituida por 'ccia_mando_63.py'.")

# Reemplazar asignaciones dinámicas por nombre de archivo dentro del bloque del artefacto 63
pattern_dict = r'(63\s*:\s*\{[^}]*?[\'"](?:script|path|file)[\'"]\s*:\s*[\'"])([^\'"]+)([\'"])'
def replacer(match):
    prefix = match.group(1)
    suffix = match.group(3)
    return f"{prefix}{new_target}{suffix}"

if re.search(pattern_dict, updated_code):
    updated_code = re.sub(pattern_dict, replacer, updated_code)
    print("  ✅ Mapeo del diccionario para clave 63 actualizado correctamente.")

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.write(updated_code)

# 2. Validar sintaxis AST
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py verificado y compilado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
