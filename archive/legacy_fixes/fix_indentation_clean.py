import py_compile

def repair_indentation_and_vars(filepath):
    print(f"🛠️ Ajustando sangría y variables en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        indent_len = len(line) - len(line.lstrip())
        indent_str = line[:indent_len]

        # 1. Corregir instrucción reemplazada preservando la sangría exacta del archivo
        if "pass  # sustituido continue" in line or stripped == "continue":
            new_lines.append(f"{indent_str}pass\n")
            continue

        # 2. Insertar definición de 'icon' con la misma sangría que el print
        if "BUCLE 24/7 ARTEFACTO 62 CAMBIADO A:" in line:
            prev_context = "".join(new_lines[-3:])
            if "icon =" not in prev_context:
                new_lines.append(f'{indent_str}icon = "🟢" if "ENABLE" in str(new_status).upper() or "ACT" in str(new_status).upper() else "🔴"\n')

        new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

repair_indentation_and_vars("/home/k1/ccia_workspace/modules/art_63.py")
repair_indentation_and_vars("/home/k1/ccia_workspace/ccia_mando_63.py")
