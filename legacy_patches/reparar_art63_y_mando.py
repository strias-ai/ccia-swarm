import sqlite3
import os
import py_compile
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("==================================================================")
print(" 🛠️ REPARACIÓN DE ARTEFACTO 63 Y SUBMENÚ (ISSUEHUNT EXCLUSIVO)")
print("==================================================================")

# 1. Reparar sangrado en modules/art_63.py
if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "def evolutionary_bounty_searcher" in line:
            fixed_lines.append("    def evolutionary_bounty_searcher(self, keywords=None):\n")
            fixed_lines.append('        """Ejecuta únicamente el scraper exclusivo de IssueHunt"""\n')
            fixed_lines.append("        try:\n")
            fixed_lines.append("            import upgrade_bounty_scraper\n")
            fixed_lines.append("            upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()\n")
            fixed_lines.append("        except Exception as e:\n")
            fixed_lines.append('            print(f"⚠️ Error ejecutando scraper IssueHunt: {e}")\n')
            
            # Saltar líneas previas desalineadas hasta la siguiente función o clase
            i += 1
            while i < len(lines) and not (lines[i].startswith("    def ") or lines[i].startswith("class ") or lines[i].startswith("def ")):
                i += 1
            continue
        else:
            fixed_lines.append(line)
            i += 1

    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    try:
        py_compile.compile(ART63_PATH, doraise=True)
        print("  🟢 'modules/art_63.py' corregido y sintaxis validada OK.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error persistente en art_63.py: {e}")

# 2. Conectar opción B en ccia_mando_63.py directamente a IssueHunt
if os.path.exists(MANDO_PATH):
    with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
        mando_code = f.read()

    # Reemplazar la ejecución de la opción 'b' o 'B' en el submenú
    mando_code = re.sub(
        r'([bB]uscador V3.*?API\.\.\.)',
        'Iniciando consulta a API GraphQL IssueHunt...',
        mando_code
    )

    # Inyectar la llamada directa a fetch_issuehunt_bounties_exclusive()
    if "fetch_issuehunt_bounties_exclusive" not in mando_code:
        mando_code = mando_code.replace(
            "evolutionary_bounty_searcher()",
            "evolutionary_bounty_searcher()\n            import upgrade_bounty_scraper\n            upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()"
        )

    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(mando_code)

    try:
        py_compile.compile(MANDO_PATH, doraise=True)
        print("  🟢 'ccia_mando_63.py' corregido y sintaxis validada OK.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error persistente en ccia_mando_63.py: {e}")

# 3. Limpieza final de la Base de Datos
conn = sqlite3.connect(DB_PATH, timeout=30.0)
c = conn.cursor()
c.execute("""
    DELETE FROM bounty_opportunities 
    WHERE repo LIKE '%bounty-plaza%' 
       OR title LIKE '%bounty-plaza%' 
       OR title LIKE '%$999999999%' 
       OR repo LIKE '%OmniBlocks%' 
       OR repo LIKE '%stellar-forge%'
""")
deleted = c.rowcount
conn.commit()
conn.close()

print(f"  🧹 Registros de spam purgados: {deleted}")
print("==================================================================")
print("🚀 SANEAMIENTO FINALIZADO. Ya puedes ejecutar ccia_mando_63.py.")
print("==================================================================")
