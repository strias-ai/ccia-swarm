import os
import py_compile
import ast

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: DIAGNÓSTICO Y REPARACIÓN DE CADENAS MULTILÍNEA (TRIPLE QUOTES)")
print("================================================================================")

def inspect_and_fix_quotes(filepath):
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return

    print(f"\n📄 Inspeccionando {filename}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Contar ocurrencias de ''' y """
    t_single_count = 0
    t_double_count = 0
    for idx, line in enumerate(lines):
        t_single_count += line.count("'''")
        t_double_count += line.count('"""')

    print(f"  • Ocurrencias de ''': {t_single_count}")
    print(f"  • Ocurrencias de \"\"\": {t_double_count}")

    # Si la cantidad de triple-quotes es impar, hay una abierta sin cerrar
    fixed = False
    if t_single_count % 2 != 0:
        print("  ⚠️ Tres comillas simples (''') desbalanceadas. Buscando cierre faltante...")
        # Recorrer de abajo arriba para cerrar la última abierta
        for idx in range(len(lines) - 1, -1, -1):
            if "'''" in lines[idx]:
                lines.insert(idx + 1, "'''\n")
                fixed = True
                break

    if t_double_count % 2 != 0:
        print("  ⚠️ Tres comillas dobles (\"\"\") desbalanceadas. Buscando cierre faltante...")
        for idx in range(len(lines) - 1, -1, -1):
            if '"""' in lines[idx]:
                lines.insert(idx + 1, '"""\n')
                fixed = True
                break

    if fixed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # Intentar compilación AST
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filename} COMPILADO Y CERTIFICADO EXITOSAMENTE.")
    except py_compile.PyCompileError as e:
        exc = e.exc_value
        lineno = getattr(exc, 'lineno', '?')
        msg = getattr(exc, 'msg', str(e))
        text = getattr(exc, 'text', '')
        print(f"  ❌ Error persistente en línea {lineno}: {msg}")
        if text:
            print(f"     Código: {text.strip()}")

for filepath in FILES:
    inspect_and_fix_quotes(filepath)

print("\n================================================================================")
print("✅ INSPECCIÓN COMPLETADA.")
print("================================================================================")
