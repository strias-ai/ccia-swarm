import py_compile

def fix_line_441(filepath):
    print(f"🔍 Auditando y corrigiendo sintaxis en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed = False
    new_lines = []
    for line in lines:
        if '{"valid": true' in line and 'check_prompt' in line:
            # Reemplazo seguro evitando conflictos de f-string y comillas
            corrected_line = '        json_spec = \'{"valid": true, "reason": "..."}\'\n        check_prompt = f"Evaluar bounty {repo}#{issue_id}. Responder estricto JSON: {json_spec}"\n'
            new_lines.append(corrected_line)
            fixed = True
        else:
            new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y CORREGIDO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error en {filepath}: {e}")

fix_line_441("/home/k1/ccia_workspace/modules/art_63.py")
fix_line_441("/home/k1/ccia_workspace/ccia_mando_63.py")
