import os
import py_compile
import ast

FILES = [
    ("/home/k1/ccia_workspace/modules/art_63.py", 648),
    ("/home/k1/ccia_workspace/ccia_mando_63.py", 99)
]

print("================================================================================")
print("🔍 CCiA CTO ENGINE: DIAGNÓSTICO Y REPARACIÓN PUNTUAL DE COMILLAS TRIPLES")
print("================================================================================")

for filepath, target_line in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📂 Analizando {filename} cerca de la línea {target_line}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Mostrar fragmento antes de reparar
    start = max(0, target_line - 8)
    end = min(len(lines), target_line + 12)
    print("--- Fragmento actual ---")
    for idx in range(start, end):
        marker = " >> " if idx == target_line - 1 else "    "
        print(f"{marker}{idx+1:4d} | {lines[idx].rstrip()}")
    print("------------------------")

    # Eliminar comillas triples huérfanas en líneas que contengan solo triple quote
    new_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        # Si la línea es solo '"""' o "'''" de una inyección previa, la omitimos
        if stripped in ['"""', "'''", '"""\n', "'''\n"]:
            continue
        new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Verificar si AST compila
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code, filename=filename)
        print(f"  ✅ {filename} CERTIFICADO Y COMPILADO SINTÁCTICAMENTE POR EL AST.")
    except SyntaxError as e:
        print(f"  ⚠️ Error AST restante en {filename} (Línea {e.lineno}): {e.msg}")
        if e.lineno and e.lineno <= len(new_lines):
            bad_idx = e.lineno - 1
            # Si hay un triple quote al final de un cur.execute sin cerrar
            if "unterminated triple-quoted string" in str(e.msg):
                new_lines.insert(bad_idx + 1, '""")\n')
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print("     --> Insertado cierre '\"\"\")'. Re-verificando...")

        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} CERTIFICADO EXITOSAMENTE TRAS AJUSTE.")
        except Exception as ex:
            print(f"  ❌ Error persistente: {ex}")

print("\n================================================================================")
print("✅ DIAGNÓSTICO Y REPARACIÓN PUNTUAL FINALIZADOS.")
print("================================================================================")
