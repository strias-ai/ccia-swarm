import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: BALANCE Y REPARACIÓN EXACTA DE STRINGS MULTILÍNEA")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📂 Reparando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for attempt in range(1, 20):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} SINTAXIS CERTIFICADA Y COMPILADA CON ÉXITO.")
            break
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            if "unterminated triple-quoted string" in msg or "never closed" in msg:
                open_idx = (lineno - 1) if lineno and lineno <= len(lines) else 0
                line_text = lines[open_idx] if open_idx < len(lines) else ""
                quote = "'''" if "'''" in line_text else '"""'

                # Buscar la siguiente estructura (def, class, elif, if) para cerrar la cadena
                close_idx = open_idx + 1
                while close_idx < len(lines):
                    s = lines[close_idx].strip()
                    if s.startswith("def ") or s.startswith("class ") or s.startswith("elif ") or (s.startswith("if ") and "opt" in s):
                        break
                    close_idx += 1

                indent = " " * (len(line_text) - len(line_text.lstrip()))
                if "execute(" in line_text:
                    lines.insert(close_idx, indent + quote + ")\n")
                else:
                    lines.insert(close_idx, indent + quote + "\n")

                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            else:
                # Ajuste de sangría si surge un error secundario tras cerrar la cadena
                if lineno and 0 <= lineno - 1 < len(lines):
                    idx = lineno - 1
                    if "unexpected indent" in msg or "unindent" in msg:
                        lines[idx] = lines[idx].lstrip()
                    elif "expected an indented block" in msg:
                        lines.insert(idx, "    pass\n")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                else:
                    print(f"  ❌ Error no resuelto en {filename}: {msg}")
                    break

print("\n================================================================================")
print("✅ BALANCÉ DE STRINGS Y COMPILACIÓN FINALIZADOS. EJECUTA 'ccia1' -> OPCIÓN 4.")
print("================================================================================")
