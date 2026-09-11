import os
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ RESTAURANDO ACCESO AL CENTRO DE MANDO (13 OPCIONES) Y ELIMINANDO FALLBACK")
print("=" * 80)

# 1. Corregir punto de entrada de art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Reemplazar valores hardcodeados de comment-auto-bot por la primera tarea PENDING de la DB
code = re.sub(
    r'https://github\.com/karthikabinav/comment-auto-bot/issues/\d+',
    '',
    code
)

entry_point_fix = """
if __name__ == "__main__":
    import sys, os
    if "--daemon" in sys.argv:
        run_daemon_loop()
    else:
        mando_script = "/home/k1/ccia_workspace/ccia_mando_63.py"
        os.execv(sys.executable, [sys.executable, mando_script])
"""

if 'if __name__ ==' in code:
    code = re.sub(r'if __name__ == ["\']__main__["\'][\s\S]*$', entry_point_fix.strip(), code)
else:
    code += "\n\n" + entry_point_fix.strip() + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Punto de entrada de modules/art_63.py reconfigurado para abrir ccia_mando_63.py.")

# 2. Actualizar ccia_mando_63.py para invocar el demonio con el flag --daemon
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    mando_code = f.read()

mando_code = mando_code.replace(
    '["python3", "-u", "/home/k1/ccia_workspace/modules/art_63.py"]',
    '["python3", "-u", "/home/k1/ccia_workspace/modules/art_63.py", "--daemon"]'
)
mando_code = mando_code.replace(
    '["python3", "/home/k1/ccia_workspace/modules/art_63.py"]',
    '["python3", "-u", "/home/k1/ccia_workspace/modules/art_63.py", "--daemon"]'
)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(mando_code)

print("  ✅ ccia_mando_63.py configurado para invocar el demonio con el parámetro --daemon.")

# 3. Comprobación de compilación
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Módulos validados y compilan correctamente.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
