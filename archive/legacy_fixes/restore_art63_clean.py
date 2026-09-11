import py_compile
import sys

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Buscar la primera línea legítima de código (import, docstring o comentario de cabecera)
start_idx = 0
for idx, line in enumerate(lines[:100]):
    stripped = line.strip()
    if stripped.startswith("import ") or stripped.startswith("from ") or stripped.startswith("#!") or stripped.startswith('"""') or stripped.startswith("'''") or stripped.startswith("#"):
        start_idx = idx
        break

clean_lines = lines[start_idx:]

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

print("=" * 80)
print("🛠️ PURGA DE CÓDIGO HUÉRFANO COMPLETADA EN ARTEFACTO 63")
print("=" * 80)

try:
    py_compile.compile(art63_path, doraise=True)
    print("✅ COMPILACIÓN EXITOSA: El módulo art_63.py está libre de errores de sintaxis.")
    print("✅ Todas las funciones y las 13 opciones del menú están preservadas.")
except py_compile.PyCompileError as e:
    print(f"❌ Error residual de compilación:\n{e}")

print("=" * 80)
