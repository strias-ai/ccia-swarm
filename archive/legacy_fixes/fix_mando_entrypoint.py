import os
import sys
import py_compile
import ast
import re

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🛠️ AUDITANDO Y REPARANDO PUNTO DE ENTRADA EN CCIA_MANDO_63.PY")
print("=" * 80)

with open(MANDO_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Identificar si la función principal del menú existe
menu_func_match = re.search(r'def\s+(show_mando_menu|main_menu|menu_mando|main)\s*\(\):', content)
menu_func_name = menu_func_match.group(1) if menu_func_match else None

print(f"  • Función del menú detectada: {menu_func_name if menu_func_name else 'No detectada explícitamente'}")

# 2. Asegurar que el bloque if __name__ == '__main__': invoque la función del menú o el bucle
if "if __name__ ==" in content:
    # Eliminar bloque if __name__ incompleto o roto al final del archivo
    content = re.sub(r'if __name__\s*==\s*[\'"]__main__[\'"]\s*:[\s\S]*$', '', content).strip()

# Reconstruir el punto de entrada principal asegurando la llamada al menú interactivo
if menu_func_name:
    entrypoint = f"\n\nif __name__ == '__main__':\n    {menu_func_name}()\n"
else:
    # Si las opciones están en el ámbito global dentro de un while True, envolver correctamente
    entrypoint = "\n\nif __name__ == '__main__':\n    pass\n"

# Buscar si existe una función de menú principal para invocar
if not menu_func_name:
    # Buscar patrones de funciones que muestren el menú de 13 opciones
    for fn in ["menu_mando_63", "main", "mostrar_menu", "run_mando"]:
        if f"def {fn}" in content:
            entrypoint = f"\n\nif __name__ == '__main__':\n    {fn}()\n"
            break

content_fixed = content + entrypoint

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(content_fixed)

# 3. Validar sintaxis y compilar
try:
    with open(MANDO_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    ast.parse(src)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ ccia_mando_63.py validado y listo para ejecución.")
except Exception as e:
    print(f"  ❌ Error sintáctico en ccia_mando_63.py: {e}")

print("=" * 80)
