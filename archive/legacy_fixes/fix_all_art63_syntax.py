import py_compile
import re

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Eliminar inyecciones de 'pass' e 'import' desalineadas tras 'def'
content = re.sub(
    r'(\n\s*def\s+\w+\s*\(.*?\):\n)\s*pass\n\s*import\s+urllib\.request, urllib\.parse, json\n',
    r'\1',
    content
)
content = re.sub(
    r'(\n\s*def\s+\w+\s*\(.*?\):\n)\s*import\s+urllib\.request, urllib\.parse, json\n',
    r'\1',
    content
)

lines = content.splitlines(True)
fixed_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # 2. Verificar que cada línea terminada en ':' tenga un bloque identado
    if stripped.endswith(":") and not stripped.startswith("#"):
        indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        
        j = i + 1
        next_indent = -1
        while j < len(lines):
            s = lines[j].strip()
            if s and not s.startswith("#"):
                next_indent = len(lines[j]) - len(lines[j].lstrip())
                break
            j += 1
            
        if next_indent <= indent:
            fixed_lines.append(" " * (indent + 4) + "pass\n")
    else:
        fixed_lines.append(line)
    i += 1

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print("=" * 80)
print("🛠️ SINTAXIS REPARADA INTEGRALMENTE EN ARTEFACTO 63")
print("=" * 80)

try:
    py_compile.compile(art63_path, doraise=True)
    print("  ✅ modules/art_63.py COMPILA CORRECTAMENTE.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación residual:\n{e}")

print("=" * 80)
