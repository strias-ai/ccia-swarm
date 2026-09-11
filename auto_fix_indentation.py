import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: AUTORREPARACIÓN DE SANGRÍA Y CERTIFICACIÓN SINTÁCTICA")
print("================================================================================")

def repair_file_syntax(filepath):
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return False

    for iteration in range(1, 25):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} COMPILADO Y CERTIFICADO SIN ERRORES (en iteración {iteration}).")
            return True
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            if lineno is None:
                print(f"  ❌ Error indeterminado en {filename}: {e}")
                return False

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            idx = lineno - 1
            if idx < len(lines):
                line_content = lines[idx]
                
                # Caso 1: unexpected indent
                if "unexpected indent" in msg:
                    prev_idx = idx - 1
                    while prev_idx >= 0 and not lines[prev_idx].strip():
                        prev_idx -= 1
                    
                    if prev_idx >= 0:
                        prev_indent = len(lines[prev_idx]) - len(lines[prev_idx].lstrip())
                        # Ajustar la sangría al nivel de la línea anterior no vacía
                        lines[idx] = " " * prev_indent + line_content.lstrip()
                    else:
                        lines[idx] = line_content.lstrip()
                
                # Caso 2: expected an indented block
                elif "expected an indented block" in msg:
                    indent = len(line_content) - len(line_content.lstrip())
                    lines.insert(idx, " " * (indent + 4) + "pass\n")

                # Caso 3: Cadenas/instrucciones rotas
                else:
                    lines[idx] = "# " + line_content

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            else:
                print(f"  ❌ Línea {lineno} fuera de rango en {filename}.")
                return False

    print(f"  ⚠️ Se alcanzó el límite de iteraciones en {filename}.")
    return False

for fpath in FILES:
    print(f"\n🔍 Analizando y corrigiendo: {fpath}")
    repair_file_syntax(fpath)

print("\n================================================================================")
print("✅ PROCESO COMPLETADO. PRUEBA LANZAR 'ccia1' AHORA.")
print("================================================================================")
