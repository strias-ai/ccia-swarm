import os
import py_compile

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"

with open(ART63_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    fixed.append(line)
    
    stripped = line.strip()
    if stripped.endswith(":") and not stripped.startswith("#"):
        current_indent = len(line) - len(line.lstrip())
        
        # Buscar la siguiente línea no vacía ni comentario
        next_idx = i + 1
        has_indented_child = False
        while next_idx < len(lines):
            next_line = lines[next_idx]
            next_stripped = next_line.strip()
            if next_stripped and not next_stripped.startswith("#"):
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > current_indent:
                    has_indented_child = True
                break
            next_idx += 1
            
        if not has_indented_child:
            indent_str = " " * (current_indent + 4)
            fixed.append(f"{indent_str}pass\n")
    i += 1

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.writelines(fixed)

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS Y BLOQUES EN ARTEFACTO 63")
print("=" * 80)

try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: modules/art_63.py validado sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
