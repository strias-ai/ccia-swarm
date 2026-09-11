import os
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ REDIRIGIENDO OPCIÓN [4] DIRECTAMENTE AL CENTRO DE MANDO (13 OPCIONES)")
print("=" * 80)

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Limpiar cualquier bloque if __name__ anterior
code = re.sub(r'\nif __name__\s*==\s*[\'"]__main__[\'"][\s\S]*$', '', code)

# Inyectar el punto de entrada con enrutamiento correcto
new_entrypoint = """

if __name__ == "__main__":
    import sys, os
    if "--daemon" in sys.argv:
        run_daemon_loop()
    elif "--submenu" in sys.argv:
        if "show_bounty_submenu" in globals():
            show_bounty_submenu()
        elif "bounty_submenu" in globals():
            bounty_submenu()
        else:
            print("🎯 [SUBMENÚ BOUNTIES] Opción de gestión de base de datos activa.")
    else:
        mando_script = "/home/k1/ccia_workspace/ccia_mando_63.py"
        if os.path.exists(mando_script):
            os.execv(sys.executable, [sys.executable, mando_script])
        else:
            print(f"❌ Error: No se encontró el centro de mando en {mando_script}")
"""

code = code.strip() + new_entrypoint

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Punto de entrada reconfigurado en modules/art_63.py.")

# Verificación de compilación
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Ambos módulos compilan correctamente.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
