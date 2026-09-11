import os
import sys
import py_compile
import ast
import re

MISSION_CONTROL_PATH = "/home/k1/ccia_mission_control.py"

print("=" * 80)
print("🛠️ VINCULANDO OPCIÓN [4] DEL ARTEFACTO 63 CON CCIA_MANDO_63.PY")
print("=" * 80)

if not os.path.exists(MISSION_CONTROL_PATH):
    print(f"❌ No se encontró el archivo {MISSION_CONTROL_PATH}")
    sys.exit(1)

with open(MISSION_CONTROL_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Reemplazar la ruta de ejecucion para el Artefacto 63 cuando se lanza el Mando y Control
old_path_1 = "/home/k1/ccia_workspace/modules/art_63.py"
new_path_1 = "/home/k1/ccia_workspace/ccia_mando_63.py"

# Buscar referencias donde el Artefacto 63 lance art_63.py y cambiar a ccia_mando_63.py
modified = False

if old_path_1 in content:
    # Asegurar que solo cambiamos cuando se trata del lanzador o la opcion 4 de art_63
    content = content.replace(old_path_1, new_path_1)
    modified = True
    print("  ✅ Ruta de lanzamiento actualizada de 'modules/art_63.py' a 'ccia_mando_63.py'.")

# Si hay referencias relativas del tipo "modules/art_63.py" dentro de la seccion del artefacto 63:
pattern = r'("art_63\.py"|\'art_63\.py\')'
if not modified and re.search(pattern, content):
    content = re.sub(pattern, '"/home/k1/ccia_workspace/ccia_mando_63.py"', content)
    modified = True
    print("  ✅ Referencia 'art_63.py' sustituida por 'ccia_mando_63.py'.")

with open(MISSION_CONTROL_PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    with open(MISSION_CONTROL_PATH, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(MISSION_CONTROL_PATH, doraise=True)
    print("  ✅ ccia_mission_control.py actualizado y verificado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
