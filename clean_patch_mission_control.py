import os
import sys
import py_compile
import ast

MISSION_CONTROL = "/home/k1/ccia_mission_control.py"

print("=" * 80)
print("🛠️ SANEAMIENTO Y REDIRECCIÓN LIMPIA DE ARTEFACTO 63 EN CCIA_MISSION_CONTROL.PY")
print("=" * 80)

with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Filtrar líneas corruptas o inyecciones previas relacionadas con mando 63
clean_lines = []
for line in lines:
    if "ccia_mando_63" in line or "str(art_id) == \"63\"" in line or "str(art_id) == '63'" in line:
        continue
    clean_lines.append(line)

# 2. Inyectar el override inmediatamente después de asignar script_path
final_lines = []
injected = False

for line in clean_lines:
    final_lines.append(line)
    if not injected and "script_path = os.path.join(" in line:
        indent_len = len(line) - len(line.lstrip())
        indent = " " * indent_len
        body_indent = " " * (indent_len + 4)
        
        final_lines.append(f"{indent}if str(art_id) == \"63\":\n")
        final_lines.append(f"{body_indent}script_path = \"/home/k1/ccia_workspace/ccia_mando_63.py\"\n")
        injected = True

with open(MISSION_CONTROL, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

# 3. Validar sintaxis AST y compilar
try:
    with open(MISSION_CONTROL, "r", encoding="utf-8") as f:
        src = f.read()
    ast.parse(src)
    py_compile.compile(MISSION_CONTROL, doraise=True)
    print("  ✅ ccia_mission_control.py restaurado y compilado con éxito.")
except Exception as e:
    print(f"  ❌ Error de sintaxis: {e}")

print("=" * 80)
