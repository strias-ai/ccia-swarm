import os
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ CORRIGIENDO INDENTACIÓN EN ARTEFACTO 63")
print("=" * 80)

# 1. Reparación de indentación en art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for idx, line in enumerate(lines):
    # Si la línea anterior termina en ':' (definición de función/bloque) y la línea actual no está sangrada ni vacía
    if idx > 0 and lines[idx - 1].strip().endswith(":") and line.strip() and not (line.startswith(" ") or line.startswith("\t")):
        fixed_lines.append("    " + line.lstrip())
    else:
        fixed_lines.append(line)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

# 2. Prueba de compilación directa
print("\n🔍 VERIFICANDO COMPILACIÓN DE MÓDULOS:")
all_ok = True

for path in [ART63_PATH, MANDO_PATH]:
    try:
        py_compile.compile(path, doraise=True)
        print(f"  ✅ {os.path.basename(path)}: Compilación sin errores.")
    except py_compile.PyCompileError as e:
        all_ok = False
        print(f"  ❌ Error en {os.path.basename(path)}:\n{e}")

if all_ok:
    print("\n✨ SISTEMA TOTALMENTE REPARADO Y COMPILADO.")
print("=" * 80)
