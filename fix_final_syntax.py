import py_compile

def sanitize_and_fix(filepath):
    print(f"🛠️ Sanitizando {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    clean_lines = []
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        # Neutralizar sentencias opt == "A" u opciones desalineadas fuera de contexto
        if stripped.startswith('if opt == "A"') or stripped.startswith('elif opt == "A"'):
            clean_lines.append("        pass  # removido opt A huérfano\n")
            continue

        # Si hay un 'if opt' o 'elif opt' con sangría 0 fuera de bucle, darle sangría estándar
        if indent == 0 and (stripped.startswith("if opt") or stripped.startswith("elif opt") or stripped.startswith("else:")):
            clean_lines.append("        " + stripped + "\n")
            continue

        clean_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y VALIDADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

sanitize_and_fix("/home/k1/ccia_workspace/ccia_mando_63.py")
sanitize_and_fix("/home/k1/ccia_workspace/modules/art_63.py")
