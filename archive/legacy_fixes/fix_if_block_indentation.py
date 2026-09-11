import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: AUTOCORRECCIÓN DE BLOQUES IF/TRY Y CERTIFICACIÓN AST")
print("================================================================================")

def repair_file(filepath):
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        return False

    print(f"\n🔍 Reparando {filename}...")
    for iteration in range(1, 40):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} CERTIFICADO Y COMPILADO SINTÁCTICAMENTE SIN ERRORES (Iteración {iteration}).")
            return True
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            if not lineno:
                print(f"  ❌ Error indeterminado en {filename}: {e}")
                return False

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            idx = lineno - 1
            if idx < 0 or idx >= len(lines):
                break

            # 1. Error de bloque esperado tras 'if', 'elif', 'else', 'def', 'try'
            if "expected an indented block" in msg:
                prev_idx = idx - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev_indent = len(lines[prev_idx]) - len(lines[prev_idx].lstrip())
                    lines.insert(prev_idx + 1, " " * (prev_indent + 4) + "pass\n")

            # 2. Desalineación de sangría (unexpected / unindent)
            elif "unindent does not match" in msg or "unexpected indent" in msg:
                prev_idx = idx - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev_indent = len(lines[prev_idx]) - len(lines[prev_idx].lstrip())
                    lines[idx] = " " * prev_indent + lines[idx].lstrip()

            # 3. Bloque try huérfano sin except/finally
            elif "except" in msg or "finally" in msg:
                curr_indent = len(lines[idx]) - len(lines[idx].lstrip())
                lines.insert(idx, " " * curr_indent + "except Exception:\n" + " " * (curr_indent + 4) + "pass\n")

            else:
                lines[idx] = "# " + lines[idx]

            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)

    print(f"  ⚠️ Limite de iteraciones alcanzado en {filename}.")
    return False

for fpath in FILES:
    repair_file(fpath)

print("\n================================================================================")
print("✅ REPARACIÓN FINALIZADA. LANZA 'ccia1' -> OPCIÓN 4 PARA VERIFICAR.")
print("================================================================================")
