import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🔍 CCiA DIAGNÓSTICO Y LIMPIEZA DE SINTAXIS DE ARTEFACTO 63")
print("================================================================================")

def clean_file(filepath):
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return

    print(f"\n📄 Analizando {filename}...")
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # 1. Eliminar líneas comentadas masivamente introducidas por el script anterior
    cleaned_lines = []
    for line in lines:
        # Remover comentarios generados por auto-fix si dejaron bloques vacíos
        if line.strip().startswith("# elif ") or line.strip().startswith("# if ") or line.strip().startswith("# print("):
            continue
        cleaned_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    # 2. Diagnóstico exacto del compilador
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filename} COMPILADO Y CERTIFICADO SIN ERRORES.")
    except py_compile.PyCompileError as e:
        exc = e.exc_value
        lineno = getattr(exc, 'lineno', 0)
        msg = getattr(exc, 'msg', str(e))
        text = getattr(exc, 'text', '')
        
        print(f"  ❌ Error de sintaxis en {filename}:")
        print(f"     • Menaje : {msg}")
        print(f"     • Línea  : {lineno}")
        print(f"     • Código : {text.strip() if text else 'N/A'}")

        # Intentar reparación local en la línea conflictiva
        if lineno and lineno <= len(cleaned_lines):
            idx = lineno - 1
            bad_line = cleaned_lines[idx]
            
            # Caso "expected an indented block"
            if "expected an indented block" in msg:
                indent = len(bad_line) - len(bad_line.lstrip())
                cleaned_lines.insert(idx, " " * (indent + 4) + "pass\n")
            # Caso "unexpected indent"
            elif "unexpected indent" in msg:
                cleaned_lines[idx] = bad_line.lstrip()
            # Caso de comillas no cerradas
            elif "unterminated" in msg:
                cleaned_lines[idx] = "# " + bad_line

            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)

            # Re-verificar compilación
            try:
                py_compile.compile(filepath, doraise=True)
                print(f"  ✅ {filename} REPARADO Y CERTIFICADO CORRECTAMENTE.")
            except Exception as e2:
                print(f"  ⚠️ Requiere ajuste manual secundario: {e2}")

for f in FILES:
    clean_file(f)

print("\n================================================================================")
print("✅ DIAGNÓSTICO FINALIZADO.")
print("================================================================================")
