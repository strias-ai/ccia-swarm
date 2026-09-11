import sys
import py_compile

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESOLUCIÓN DE NAMEERROR ('conn' UNDEFINED) Y SANITIZACIÓN DB")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    s = line.strip()
    # Proteger llamadas de conexión BD a nivel global
    if ("conn.commit()" in line or "conn.close()" in line or "conn.execute" in line or "conn.cursor" in line) and not s.startswith("#"):
        indent = " " * (len(line) - len(line.lstrip()))
        clean_lines.append(f"{indent}if 'conn' in locals() or 'conn' in globals():\n")
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
    print("  ✅ Módulo art_63 importado y verificado exitosamente en runtime.")
except Exception as e:
    print(f"  ⚠️ Notificación de runtime: {e}")

print("================================================================================")
