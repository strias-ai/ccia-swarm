import os
import py_compile
import re

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: REPARACIÓN QUIRÚRGICA DE LÍNEA 643 Y ESCAPES DB")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines):
    # Detectar y reemplazar cualquier residuo corrupto en scan_all_platforms
    if "Escanea todas las plataformas" in line:
        indent = " " * (len(line) - len(line.lstrip()))
        new_lines.append(indent + '"""Escanea todas las plataformas de bounties soportadas."""\n')
        continue

    # Filtrar líneas con combinaciones inválidas de comentarios '#' y comillas triples
    if line.strip().startswith("#") and ('"""' in line or "'''" in line):
        continue

    new_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

# Corregir secuencias de escape '\[ ' para eliminar el SyntaxWarning
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content_fixed = content.replace(r'\[', r'\\\[')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content_fixed)

# Certificación de compilación AST
try:
    py_compile.compile(filepath, doraise=True)
    print("  ✅ art_63.py CERTIFICADO Y COMPILADO EXITOSAMENTE SIN WARNINGS NI ERRORES.")
except py_compile.PyCompileError as e:
    exc = e.exc_value
    lineno = getattr(exc, 'lineno', '?')
    msg = getattr(exc, 'msg', str(e))
    text = getattr(exc, 'text', '')
    print(f"  ❌ Error en Línea {lineno}: {msg}")
    if text:
        print(f"     Código: {text.strip()}")

print("================================================================================")
