import re
import py_compile
import ast

ART63 = "/home/k1/ccia_workspace/modules/art_63.py"
MANDO = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESTAURACIÓN Y DESBLOQUEO DEL MENÚ DE 12 OPCIONES")
print("================================================================================")

def audit_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    commented_menu_lines = [i+1 for i, l in enumerate(lines) if "#" in l and ("opt ==" in l or "Opciones" in l or "12" in l or "cartera" in l.lower() or "cerebro" in l.lower())]
    print(f"📄 {filepath}: {len(commented_menu_lines)} líneas de menú comentadas detectadas.")
    return lines

art_lines = audit_file(ART63)
mando_lines = audit_file(MANDO)

# Descomentar líneas de menú desactivadas en art_63.py
restored_art = []
for line in art_lines:
    s = line.strip()
    if s.startswith("#") and any(k in s for k in ["opt ==", "elif opt", "if opt", "print(", "Ollama", "models", "cartera", "bounty"]):
        # Descomentar solo si parece código de control
        uncommented = line.replace("# ", "", 1).replace("#", "", 1)
        restored_art.append(uncommented)
    else:
        restored_art.append(line)

with open(ART63, "w", encoding="utf-8") as f:
    f.writelines(restored_art)

# Sanitizar y verificar compilación AST
try:
    ast.parse("".join(restored_art), filename="art_63.py")
    py_compile.compile(ART63, doraise=True)
    print("  ✅ art_63.py RESTAURADO Y CERTIFICADO EXITOSAMENTE.")
except Exception as e:
    print(f"  ⚠️ Ajuste sintáctico necesario tras descomentar: {e}")

print("================================================================================")
