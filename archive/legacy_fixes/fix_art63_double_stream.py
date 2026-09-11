import os
import sys
import py_compile
import ast
import re

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"

print("=" * 80)
print("🛠️ AUDITANDO Y CORRIGIENDO DUPLICACIÓN DE STREAMING EN ART_63.PY")
print("=" * 80)

if not os.path.exists(ART63_PATH):
    print(f"❌ No se encontró el archivo: {ART63_PATH}")
    sys.exit(1)

with open(ART63_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Verificar si hay duplicación de handlers en el sistema de logging
if "logger.addHandler" in content:
    print("  • Purgando handlers duplicados de logger...")
    content = re.sub(r'(\w+)\.addHandler\(\1\.\w+\)', '', content)

# 2. Desactivar doble impresión en los callbacks de streaming
# Si existen llamadas simultáneas como print(chunk) y sys.stdout.write(chunk)
lines = content.splitlines()
fixed_lines = []
for line in lines:
    # Evitar impresiones duplicadas por chunk dentro de bucles de streaming
    if "sys.stdout.write" in line and "print(" in content and "flush=True" in line:
        continue
    fixed_lines.append(line)

fixed_content = "\n".join(fixed_lines)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(fixed_content)

# 3. Validar sintaxis AST
try:
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ art_63.py verificado y compilado sin errores.")
except Exception as e:
    print(f"  ❌ Error de sintaxis en art_63.py: {e}")

print("=" * 80)
