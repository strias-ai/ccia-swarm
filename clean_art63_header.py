art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Filtrar fragmentos huérfanos inyectados fuera de funciones en las primeras 40 líneas
clean_lines = []
for i, line in enumerate(lines):
    if i < 45 and (
        line.strip().startswith('repo_files_summary = "') 
        or 'files_out[:30]' in line 
        or line.strip() == 'repo_files_summary = ""'
        or line.strip() == 'try:'
        or line.strip() == 'except Exception:'
    ):
        continue
    clean_lines.append(line)

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

print("✅ Cabecera de art_63.py limpiada.")
