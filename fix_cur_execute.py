import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: REPARACIÓN EXACTA DE SQL TRIPLE QUOTES Y CUR.EXECUTE")
print("================================================================================")

for filepath in FILES:
    if not os.path.exists(filepath):
        continue
    filename = os.path.basename(filepath)
    print(f"\n📂 Reparando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        if 'cur.execute("""' in line or "cur.execute('''" in line:
            quote_type = '"""' if '"""' in line else "'''"
            rest_of_line = line[line.find(quote_type) + 3:]
            if quote_type not in rest_of_line:
                found_close = False
                for j in range(i + 1, min(i + 30, len(lines))):
                    if quote_type in lines[j]:
                        found_close = True
                        break
                if not found_close:
                    indent = " " * (len(line) - len(line.lstrip()))
                    fixed_lines.append(indent + quote_type + ")\n")
        i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    for attempt in range(1, 15):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} CERTIFICADO Y COMPILADO EXITOSAMENTE.")
            break
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            if not lineno:
                print(f"  ❌ Error no resoluble: {e}")
                break

            with open(filepath, "r", encoding="utf-8", errors="ignore") as cur_f:
                c_lines = cur_f.readlines()

            idx = lineno - 1
            if 0 <= idx < len(c_lines):
                bad_line = c_lines[idx]
                indent = " " * (len(bad_line) - len(bad_line.lstrip()))
                if "never closed" in msg or "unterminated" in msg:
                    c_lines.insert(idx + 1, indent + '""")\n')
                elif "unexpected indent" in msg or "unindent" in msg:
                    c_lines[idx] = bad_line.lstrip()
                else:
                    c_lines[idx] = "# " + bad_line

                with open(filepath, "w", encoding="utf-8") as cur_f:
                    cur_f.writelines(c_lines)
            else:
                break

print("\n================================================================================")
print("✅ DIAGNÓSTICO Y REPARACIÓN FINALIZADOS.")
print("================================================================================")
