import os
import py_compile

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: PURGA Y SANITIZACIÓN DEFINITIVA DE ART_63.PY")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

clean_lines = []
for idx, line in enumerate(lines):
    stripped = line.strip()
    
    # Reparar líneas corruptas por múltiples '#' acumulados
    if "# #" in line and '"""' in line:
        indent = " " * (len(line) - len(line.lstrip()))
        if "Escanea todas las plataformas" in line:
            clean_lines.append(indent + '"""Escanea todas las plataformas de bounties soportadas."""\n')
        else:
            clean_lines.append(indent + 'pass\n')
        continue
    
    if stripped.startswith("# # # #"):
        continue

    clean_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

# Reemplazar cadenas de SQL con prefijo r""" para eliminar SyntaxWarning de escapes \[
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('cur.execute("""', 'cur.execute(r"""')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Certificación de compilación AST
try:
    py_compile.compile(filepath, doraise=True)
    print("  ✅ art_63.py SANITIZADO, COMPILADO Y CERTIFICADO EXITOSAMENTE.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error sintáctico restante: {e.exc_value}")

print("================================================================================")
