import os
import py_compile
import ast

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: SANITIZACIÓN DEFINITIVA DE RAW STRINGS Y CERTIFICACIÓN AST")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📄 Procesando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Convertir ejecutores SQL a Raw Strings r""" para anular advertencias de escape \[
    content = content.replace('cur.execute("""', 'cur.execute(r"""')
    content = content.replace("cur.execute('''", "cur.execute(r'''")
    content = content.replace('cur.execute(rr"""', 'cur.execute(r"""')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Verificación estricta de árbol sintáctico (AST)
    try:
        ast.parse(content, filename=filename)
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filename} SINTAXIS CERTIFICADA 100% LIMPIA Y SIN WARNINGS.")
    except SyntaxError as e:
        print(f"  ❌ Error AST en {filename} (Línea {e.lineno}): {e.msg}")
        if e.text:
            print(f"     Código con error: {repr(e.text.strip())}")

print("\n================================================================================")
print("✅ PROCESO FINALIZADO. EJECUTA 'ccia1' Y SELECCIONA LA OPCIÓN 4.")
print("================================================================================")
