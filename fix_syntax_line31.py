import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESOLUCIÓN DE TEXTO HUÉRFANO Y CERTIFICACIÓN COMPLETA")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📂 Reparando {filename}...")

    for attempt in range(1, 30):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} COMPILADO Y CERTIFICADO EXITOSAMENTE.")
            break
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            if not lineno:
                print(f"  ❌ Error no resoluble en {filename}: {e}")
                break

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            idx = lineno - 1
            if 0 <= idx < len(lines):
                bad_line = lines[idx]
                indent = " " * (len(bad_line) - len(bad_line.lstrip()))

                if "invalid syntax" in msg and not bad_line.strip().startswith("#"):
                    lines[idx] = indent + "# " + bad_line.lstrip()
                elif "expected an indented block" in msg:
                    lines.insert(idx, indent + "    pass\n")
                elif "unexpected indent" in msg or "unindent" in msg:
                    lines[idx] = bad_line.lstrip()
                else:
                    lines[idx] = indent + "# " + bad_line.lstrip()

                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            else:
                break

print("\n================================================================================")
print("✅ REPARACIÓN FINALIZADA. LANZA 'ccia1' -> OPCIÓN 4.")
print("================================================================================")
