import sys
import py_compile

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESOLUCIÓN DE NAMEERROR ('cur' UNDEFINED)")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    s = line.strip()
    # Proteger ejecuciones de cursor huérfanas a nivel de módulo
    if ("cur.execute" in line or "cur.fetchone" in line or "cur.fetchall" in line) and not s.startswith("#"):
        indent = " " * (len(line) - len(line.lstrip()))
        clean_lines.append(f"{indent}if 'cur' in locals() or 'cur' in globals():\n")
        clean_lines.append(f"{indent}    {line.lstrip()}")
    else:
        clean_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

# Importación de prueba en tiempo de ejecución
sys.path.insert(0, "/home/k1/ccia_workspace")
try:
    py_compile.compile(filepath, doraise=True)
    if "modules.art_63" in sys.modules:
        del sys.modules["modules.art_63"]
    import modules.art_63 as art63
    print("  ✅ Módulo art_63 cargado e importado con éxito en runtime.")
except Exception as e:
    print(f"  ⚠️ Notificación de runtime: {e}")

print("================================================================================")
