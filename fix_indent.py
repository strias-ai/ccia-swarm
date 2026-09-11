art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # Corregir sangría accidental en las primeras 30 líneas a nivel global
    if i < 30 and line.startswith("        ") and "repo_files_summary" in line:
        fixed_lines.append(line.lstrip())
    else:
        fixed_lines.append(line)

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print("✅ Sangría corregida en la cabecera de art_63.py")
