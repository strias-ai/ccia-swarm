import py_compile

def fix_opt(filepath):
    print(f"🛠️ Corrigiendo NameError 'opt' en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        # Sangrar bloques condicionales 'opt' que quedaron fuera del bucle principal
        if indent == 0 and (stripped.startswith("if opt") or stripped.startswith("elif opt") or stripped == "else:"):
            fixed_lines.append("        " + stripped + "\n")
        elif indent == 0 and stripped.startswith("opt ="):
            fixed_lines.append("        " + stripped + "\n")
        else:
            fixed_lines.append(line)

    content = "".join(fixed_lines)

    # Inicializar la variable 'opt' al inicio de show_mando_menu() para prevenir NameError
    if "def show_mando_menu" in content and 'opt = ""' not in content:
        content = content.replace("def show_mando_menu():", 'def show_mando_menu():\n    opt = ""')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y VALIDADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

fix_opt("/home/k1/ccia_workspace/ccia_mando_63.py")
fix_opt("/home/k1/ccia_workspace/modules/art_63.py")
