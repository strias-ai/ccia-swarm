import re
import sys

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

print("=" * 80)
print("🛠️ RECONSTRUYENDO BLOQUE TRY/EXCEPT EN ARTEFACTO 63")
print("=" * 80)

# Bloque limpio con indentación y manejador de excepciones correcto
clean_block = '''        repo_files_summary = ""
        try:
            if 'repo_dir' in locals() and os.path.exists(repo_dir):
                import subprocess
                files_out = subprocess.check_output(
                    ["git", "-C", repo_dir, "ls-files"], stderr=subprocess.DEVNULL
                ).decode("utf-8").splitlines()
                repo_files_summary = "\\n".join(files_out[:30])
            else:
                repo_files_summary = "Directorio de repositorio no encontrado."
        except Exception:
            repo_files_summary = "No se pudo listar la estructura de archivos."
'''

# Reemplazar la sección corrupta entre repo_files_summary y la asignación del prompt
pattern = r'repo_files_summary\s*=.*?(?=prompt\s*=)'

if re.search(pattern, code, flags=re.DOTALL):
    code = re.sub(pattern, clean_block + "\n        ", code, flags=re.DOTALL)
    print("  ✅ Estructura try/except reconstruida con éxito.")
else:
    # Método alternativo por filtrado de líneas si el patrón no coincide exactamente
    lines = code.splitlines()
    new_lines = []
    inside_corrupt_zone = False
    for line in lines:
        if "repo_files_summary" in line or ("try:" in line and "files_out" in code[code.find(line):code.find(line)+200]):
            if not inside_corrupt_zone:
                new_lines.append(clean_block)
                inside_corrupt_zone = True
        elif inside_corrupt_zone and "prompt =" in line:
            inside_corrupt_zone = False
            new_lines.append(line)
        elif not inside_corrupt_zone:
            new_lines.append(line)
    code = "\n".join(new_lines)
    print("  ✅ Reemplazo por flujo de líneas completado.")

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("=" * 80)
