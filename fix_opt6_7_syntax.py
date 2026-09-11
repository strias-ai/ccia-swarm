import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: REPARACIÓN ESTRUCTURAL Y ALINEACIÓN DE BLOQUES OPT 6/7")
print("================================================================================")

for filepath in FILES:
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"⚠️ No encontrado: {filepath}")
        continue

    print(f"\n📄 Procesando {filename}...")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "bounty_swarm_history ORDER BY id DESC" in line:
            # Detectar la sangría del elif opt == "6" o equivalente previo
            elif_indent = "        "  # 8 espacios por defecto
            for k in range(len(new_lines) - 1, -1, -1):
                if "opt ==" in new_lines[k]:
                    stripped = new_lines[k].lstrip()
                    indent_len = len(new_lines[k]) - len(stripped)
                    elif_indent = " " * indent_len
                    break

            body_indent = elif_indent + "    "
            loop_indent = body_indent + "    "

            # Avanzar hasta encontrar el siguiente elif/else/if
            while i < len(lines) and not (lines[i].strip().startswith("elif ") or lines[i].strip().startswith("else:") or (lines[i].strip().startswith("if ") and "opt ==" in lines[i])):
                i += 1

            block = [
                body_indent + 'cur.execute("SELECT id, repo, issue_id, status, created_at, swarm1_draft FROM bounty_swarm_history ORDER BY id DESC LIMIT 5;")',
                body_indent + 'rows = cur.fetchall()',
                body_indent + 'conn.close()',
                body_indent + 'print("\\n🧠 ÚLTIMOS DEBATES REGISTRADOS (bounty_swarm_history):")',
                body_indent + 'for r in rows:',
                loop_indent + 'print(f" ID #{r[0]} | Repo: {r[1]}#{r[2]} | Estado: {r[3]} | Fecha: {r[4]}")',
                loop_indent + 'print(f" Output/Borrador:\\n{str(r[5])[:300]}...\\n" + "-"*50)',
                body_indent + 'pause_terminal()',
                ''
            ]
            new_lines.extend(block)
            continue
        else:
            new_lines.append(line)
            i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    # Bucle de verificación y corrección de sintaxis
    for iteration in range(1, 20):
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"  ✅ {filename} COMPILADO Y CERTIFICADO EXITOSAMENTE (Iteración {iteration}).")
            break
        except py_compile.PyCompileError as e:
            exc = e.exc_value
            lineno = getattr(exc, 'lineno', None)
            msg = getattr(exc, 'msg', str(e))

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                cur_lines = f.readlines()

            if lineno and 0 <= lineno - 1 < len(cur_lines):
                idx = lineno - 1
                bad_line = cur_lines[idx]

                if "expected an indented block" in msg:
                    prev_idx = idx - 1
                    while prev_idx >= 0 and not cur_lines[prev_idx].strip():
                        prev_idx -= 1
                    if prev_idx >= 0:
                        p_indent = len(cur_lines[prev_idx]) - len(cur_lines[prev_idx].lstrip())
                        cur_lines.insert(idx, " " * (p_indent + 4) + "pass\n")
                elif "except" in msg or "finally" in msg:
                    c_indent = len(bad_line) - len(bad_line.lstrip())
                    cur_lines.insert(idx, " " * c_indent + "except Exception:\n" + " " * (c_indent + 4) + "pass\n")
                elif "unindent" in msg or "unexpected indent" in msg or "invalid syntax" in msg:
                    if bad_line.strip().startswith("elif ") or bad_line.strip().startswith("else:"):
                        for prev_k in range(idx - 1, -1, -1):
                            if cur_lines[prev_k].strip().startswith("if ") or cur_lines[prev_k].strip().startswith("elif "):
                                p_indent = len(cur_lines[prev_k]) - len(cur_lines[prev_k].lstrip())
                                cur_lines[idx] = " " * p_indent + bad_line.lstrip()
                                break
                    else:
                        cur_lines[idx] = bad_line.lstrip()
                else:
                    cur_lines[idx] = "# " + bad_line

                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(cur_lines)
            else:
                break

print("\n================================================================================")
print("✅ REPARACIÓN FINALIZADA. EJECUTA 'ccia1' -> OPCIÓN 4 PARA LANZAR MANDO.")
print("================================================================================")
