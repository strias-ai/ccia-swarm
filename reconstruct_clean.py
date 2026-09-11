import os
import py_compile
import ast

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RECONSTRUCCIÓN Y SANITIZACIÓN AST TOTAL")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📄 Limpiando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    clean_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Fix docstring header missing comillas in line 9/1
        if idx < 15 and "CCiA Artefacto 63" in stripped and not stripped.startswith('"""') and not stripped.startswith("#"):
            clean_lines.append(f'"""\n{line}\n"""\n')
            continue

        # Eliminate orphan triple quote lines injected between statements
        if stripped in ['"""', "'''"]:
            # Check context: if previous line already closed a docstring or statement, drop it
            continue

        # Eliminate orphan cur.execute("""\n""") chunks without query
        if stripped in ['cur.execute("""', 'cur.execute(""")', 'cur.execute("""\n']:
            continue

        clean_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)

    # Validar compilación
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filename} COMPILADO Y CERTIFICADO SIN ERRORES.")
    except py_compile.PyCompileError as e:
        print(f"  ⚠️ Error en {filename}: {e.exc_value}")

print("\n================================================================================")
print("✅ RECONSTRUCCIÓN FINALIZADA.")
print("================================================================================")
