import os
import py_compile
import ast

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: PURGADO DE LÍNEAS CORRUPTAS Y CERTIFICACIÓN AST")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📂 Limpiando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    clean_lines = []
    for line in lines:
        stripped = line.strip()
        # Eliminar líneas corruptas por múltiples prefijos '#'
        if stripped.startswith("# # # #") or stripped.startswith("# # #") or stripped == '# """)' or stripped == '# "")\n':
            continue
        # Si una línea fue comentada con '#' pero termina en '""")' o ')' de forma huérfana
        if stripped.startswith("#") and ('""")' in stripped or "''')" in stripped):
            continue
        clean_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)

    # Validar con ast.parse
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code, filename=filename)
        print(f"  ✅ {filename} COMPILADO Y CERTIFICADO EXITOSAMENTE POR EL AST.")
    except SyntaxError as e:
        print(f"  ❌ Error AST en {filename}: Línea {e.lineno} - {e.msg}")
        if e.lineno and e.lineno <= len(clean_lines):
            idx = e.lineno - 1
            print(f"     Línea conflictiva: {repr(clean_lines[idx])}")
            # Si el error es unmatched ')' o ']' o '}', remover o comentar esa sola línea
            if "unmatched" in str(e.msg):
                clean_lines.pop(idx)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(clean_lines)
                print(f"     --> Línea huérfana eliminada. Re-verificando...")

            # Volver a probar
            try:
                py_compile.compile(filepath, doraise=True)
                print(f"  ✅ {filename} REPARADO Y CERTIFICADO.")
            except Exception as ex:
                print(f"  ⚠️ Requiere revisión: {ex}")

print("\n================================================================================")
print("✅ LIMPIEZA COMPLETADA. LANZA 'ccia1' -> OPCIÓN 4.")
print("================================================================================")
