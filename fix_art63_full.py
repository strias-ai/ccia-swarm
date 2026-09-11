import os
import re
import sys

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS Y LÍNEA 439 EN ARTEFACTO 63")
print("=" * 80)

if not os.path.exists(art63_path):
    print(f"❌ No se encontró {art63_path}")
    sys.exit(1)

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # Corregir la comilla no cerrada en la línea 439 / coincidencia de files_out
    if "files_out[:30]" in line and (".join" in line or line.strip().startswith('".join')):
        fixed_lines.append('        repo_files_summary = "\\n".join(files_out[:30]) if "files_out" in locals() else ""\n')
    else:
        fixed_lines.append(line)

content = "".join(fixed_lines)

# Limpiar cualquier residuo de comillas multilínea sin cerrar
content = re.sub(r'repo_files_summary\s*=\s*"\s*\n', 'repo_files_summary = ""\n', content)

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(content)

print("  ✅ Archivo modules/art_63.py corregido.")
print("=" * 80)
