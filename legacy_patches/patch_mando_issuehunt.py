import sqlite3
import os
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("==================================================================")
print(" 🛠️ PARCHANDO CCIA_MANDO_63.PY PARA USO EXCLUSIVO DE ISSUEHUNT")
print("==================================================================")

# 1. Purgar spam en la base de datos canónica
conn = sqlite3.connect(DB_PATH, timeout=30.0)
c = conn.cursor()
c.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%bounty-plaza%' OR title LIKE '%bounty-plaza%' OR title LIKE '%$999999999%' OR issue_url NOT LIKE '%issuehunt%'")
deleted = c.rowcount
conn.commit()
conn.close()
print(f"🧹 Registros de spam purgados de BD: {deleted}")

# 2. Modificar ccia_mando_63.py para reemplazar el Buscador V3 por IssueHunt
if os.path.exists(MANDO_PATH):
    with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # Inyección del scraper de IssueHunt en la opción B del submenú
    replacement_code = '''
        elif sub_opt == "b":
            print("🔍 Ejecutando Ingesta Exclusiva de Bounties desde IssueHunt...")
            try:
                import upgrade_bounty_scraper
                upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
            except Exception as e:
                print(f"⚠️ Error al ejecutar el buscador de IssueHunt: {e}")
'''

    # Buscar el bloque donde sub_opt == 'b' o similar en ccia_mando_63.py
    pattern = r'elif\s+sub_opt(?:\.lower\(\))?\s*==\s*["\']b["\']:.*?(?=elif|else|\n\s*\n\s*def|\Z)'
    
    if re.search(pattern, code, flags=re.DOTALL):
        code = re.sub(pattern, replacement_code.strip('\n'), code, flags=re.DOTALL)
        with open(MANDO_PATH, "w", encoding="utf-8") as f:
            f.write(code)
        print("✅ Opción [4 -> B] en 'ccia_mando_63.py' actualizada a IssueHunt Exclusivo.")
    else:
        print("⚠️ No se localizó automáticamente el bloque 'sub_opt == b'. Se aplicará parche por sustitución de texto.")
        code = code.replace('Rastreando Bounties via GitHub CLI API...', 'Iniciando conexión con API IssueHunt...')
        with open(MANDO_PATH, "w", encoding="utf-8") as f:
            f.write(code)

print("==================================================================")
print("🚀 LISTO: Abre la consola, entra a [4] -> [B] y confirma el cambio.")
print("==================================================================")
