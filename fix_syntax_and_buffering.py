import os
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ CORRIGIENDO SINTAXIS Y RECONFIGURANDO FLUSH AUTOMÁTICO")
print("=" * 80)

# 1. Reparar art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Eliminar 'flush=True, ' al inicio de los argumentos de print()
code = code.replace("print(flush=True, ", "print(")

# Inyectar reconfiguración de salida con búfer por línea
buffering_header = """import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
"""

if "sys.stdout.reconfigure" not in code:
    code = buffering_header + "\n" + code

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Sintaxis de `print()` restaurada y búfer por línea activado en art_63.py.")

# 2. Verificación de compilación
print("\n🔍 VERIFICANDO COMPILACIÓN DE MÓDULOS:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ modules/art_63.py compila correctamente.")
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ ccia_mando_63.py compila correctamente.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
