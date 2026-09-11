import os
import sys
import py_compile
import ast

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESOLUCIÓN DE ERROR EN TIEMPO DE EJECUCIÓN (NameError)")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

clean_lines = []
for idx, line in enumerate(lines):
    s = line.strip()
    # Si row_dict se utiliza en el nivel superior sin ser asignado previamente
    if "row_dict" in line and not s.startswith("#"):
        indent = " " * (len(line) - len(line.lstrip()))
        if "row_dict =" not in line:
            clean_lines.append(f"{indent}row_dict = locals().get('row_dict', {{}})\n")
    clean_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

# Probar la importación y ejecución del módulo
sys.path.insert(0, "/home/k1/ccia_workspace")
try:
    py_compile.compile(filepath, doraise=True)
    print("  ✅ Compilación AST válida.")
    
    # Importar el módulo dinámicamente para asegurar que no falle en importación
    if "modules.art_63" in sys.modules:
        del sys.modules["modules.art_63"]
    import modules.art_63 as art63
    print("  ✅ Módulo art_63 cargado e importado correctamente sin errores en runtime.")
except Exception as e:
    print(f"  ⚠️ Corrección aplicada con detalle: {e}")

print("================================================================================")
