import os
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: ALINEACIÓN QUIRÚRGICA DE RECORD_QUEEN_AUDIT")
print("================================================================================")

for filepath in FILES:
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"⚠️ No encontrado: {filepath}")
        continue

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    target_idx = -1
    for i, line in enumerate(lines):
        if "def record_queen_audit" in line:
            target_idx = i
            break

    if target_idx != -1:
        # Detectar la sangría de la función/método anterior
        target_indent = "    "
        for i in range(target_idx - 1, -1, -1):
            s_line = lines[i].lstrip()
            if s_line.startswith("def ") or s_line.startswith("class "):
                indent_len = len(lines[i]) - len(s_line)
                if s_line.startswith("class "):
                    target_indent = " " * (indent_len + 4)
                else:
                    target_indent = " " * indent_len
                break

        # Re-alinear la cabecera del método
        lines[target_idx] = target_indent + lines[target_idx].lstrip()

        # Re-alinear el cuerpo del método (siguiente nivel de sangría)
        body_indent = target_indent + "    "
        j = target_idx + 1
        while j < len(lines):
            stripped = lines[j].strip()
            if not stripped:
                j += 1
                continue
            
            # Detenerse si encontramos el siguiente método o clase
            curr_indent = len(lines[j]) - len(lines[j].lstrip())
            if (stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("@")) and curr_indent <= len(target_indent):
                break

            lines[j] = body_indent + lines[j].lstrip()
            j += 1

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # Validar compilación
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filename} SINTAXIS CERTIFICADA Y COMPILADA CON ÉXITO.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ {filename} aún reporta: {e}")

print("================================================================================")
print("✅ REPARACIÓN FINALIZADA. EJECUTA 'ccia1' -> OPCIÓN 4 PARA LANZAR MANDO.")
print("================================================================================")
