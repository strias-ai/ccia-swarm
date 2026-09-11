import py_compile
import ast

filepath = "/home/k1/ccia_workspace/modules/art_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: BALANCE DE COMILLAS TRIPLES Y CERTIFICACIÓN AST")
print("================================================================================")

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    stripped = line.strip()
    if "# #" in line or (stripped.startswith("#") and ('"""' in line or "'''" in line)):
        continue
    clean_lines.append(line)

final_lines = []
in_dquote = False
in_squote = False

for line in clean_lines:
    s = line.strip()
    
    # Cerrar cadenas triples pendientes antes de la declaración de nuevas funciones o bloques
    if (s.startswith("def ") or s.startswith("class ") or s.startswith("if __name__")) and (in_dquote or in_squote):
        if in_dquote:
            final_lines.append('    """)\n' if "execute" in "".join(final_lines[-5:]) else '    """\n')
            in_dquote = False
        if in_squote:
            final_lines.append("    ''')\n" if "execute" in "".join(final_lines[-5:]) else "    '''\n")
            in_squote = False

    dq_count = line.count('"""')
    sq_count = line.count("'''")

    if dq_count % 2 != 0:
        in_dquote = not in_dquote
    if sq_count % 2 != 0:
        in_squote = not in_squote

    final_lines.append(line)

if in_dquote:
    final_lines.append('""")\n')
if in_squote:
    final_lines.append("''')\n")

content = "".join(final_lines)
content = content.replace(r'\[', r'\\\[')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content, filename="art_63.py")
    py_compile.compile(filepath, doraise=True)
    print("  ✅ art_63.py COMPILADO Y CERTIFICADO EXITOSAMENTE POR EL AST.")
except SyntaxError as e:
    print(f"  ❌ Error AST en línea {e.lineno}: {e.msg}")
    if e.lineno and e.lineno <= len(final_lines):
        print(f"     Línea conflictiva ({e.lineno}): {repr(final_lines[e.lineno - 1].strip())}")

print("================================================================================")
