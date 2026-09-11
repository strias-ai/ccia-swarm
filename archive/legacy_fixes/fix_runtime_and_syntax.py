import py_compile
import re

def fix_icon_in_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Definir la variable 'icon' antes de su uso en toggle_art62_247
    target = 'print(f"\\n{icon} BUCLE 24/7 ARTEFACTO 62 CAMBIADO A: [{new_status}]")'
    replacement = 'icon = "🟢" if "ENABLE" in str(new_status).upper() or "ACT" in str(new_status).upper() else "🔴"\n        print(f"\\n{icon} BUCLE 24/7 ARTEFACTO 62 CAMBIADO A: [{new_status}]")'

    if target in content:
        content = content.replace(target, replacement)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ Corregido NameError 'icon' en {filepath}")

def fix_orphan_continue(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        if line.strip() == "continue":
            fixed_lines.append("            pass  # sustituido continue huérfano\n")
        else:
            fixed_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y VALIDADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error de compilación en {filepath}: {e}")

print("🛠️ Aplicando parches de tiempo de ejecución y sintaxis...")
fix_icon_in_file("/home/k1/ccia_workspace/modules/art_63.py")
fix_icon_in_file("/home/k1/ccia_workspace/ccia_mando_63.py")

fix_orphan_continue("/home/k1/ccia_workspace/ccia_mando_63.py")
fix_orphan_continue("/home/k1/ccia_workspace/modules/art_63.py")
