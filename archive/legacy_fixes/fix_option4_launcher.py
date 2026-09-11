import os
import re
import sys
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("=" * 80)
print("🛠️ CORRIGIENDO PUNTO DE ENTRADA Y REDIRECCIÓN DE LA OPCIÓN [4]")
print("=" * 80)

# 1. Configurar art_63.py para que al ejecutarse directamente abra ccia_mando_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

entry_block = """
if __name__ == "__main__":
    import subprocess
    mando_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ccia_mando_63.py")
    if os.path.exists(mando_script):
        subprocess.run([sys.executable, mando_script])
    else:
        print("❌ Error: No se encontró ccia_mando_63.py")
"""

if 'if __name__ ==' in code:
    code = re.sub(r'if __name__ == ["\']__main__["\'][\s\S]*$', entry_block.strip(), code)
else:
    code = code + "\n\n" + entry_block.strip() + "\n"

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Punto de entrada en modules/art_63.py restaurado correctamente.")

# 2. Buscar lanzadores en el workspace y actualizar rutas para llamar a ccia_mando_63.py
updated_files = 0
for root, dirs, files in os.walk(WORKSPACE):
    for file in files:
        if file.endswith(".py") and file not in ["fix_option4_launcher.py", "art_63.py"]:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                if "modules/art_63.py" in content or "art_63.py" in content:
                    # Sustituir llamadas de subproceso de art_63 por ccia_mando_63
                    new_content = re.sub(r'(subprocess\.(?:run|Popen|call)\(\[[^\]]*)"modules/art_63\.py"', r'\1"ccia_mando_63.py"', content)
                    new_content = re.sub(r'(subprocess\.(?:run|Popen|call)\(\[[^\]]*)"art_63\.py"', r'\1"ccia_mando_63.py"', new_content)
                    
                    if new_content != content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"  ✅ Lanzador actualizado: {os.path.basename(filepath)}")
                        updated_files += 1
            except Exception:
                pass

# 3. Verificación de compilación
print("\n🔍 VERIFICANDO SINTAXIS Y COMPILACIÓN:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Todos los componentes compilan sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación: {e}")

print("=" * 80)
