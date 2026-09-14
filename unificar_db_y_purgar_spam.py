import sqlite3
import os
import re

WORKSPACE = "/home/k1/ccia_workspace"
CANONICAL_DB = os.path.join(WORKSPACE, "ccia_bounties.db")

print("==================================================================")
print(" 🔍 AUDITORÍA DE BASES DE DATOS Y UNIFICACIÓN DE RUTAS")
print("==================================================================")

# 1. Localizar todos los archivos .db en el workspace
db_files = []
for root, _, files in os.walk(WORKSPACE):
    for f in files:
        if f.endswith(".db"):
            db_files.append(os.path.join(root, f))

print(f"📦 Bases de datos detectadas ({len(db_files)}):")
for db in db_files:
    print(f"  • {db}")
    try:
        conn = sqlite3.connect(db, timeout=5.0)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in c.fetchall()]
        if "bounty_opportunities" in tables:
            c.execute("SELECT COUNT(*) FROM bounty_opportunities")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE title LIKE '%bounty-plaza%' OR title LIKE '%$999999999%'")
            spam = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE issue_url LIKE '%issuehunt%' OR title LIKE '%IssueHunt%'")
            issuehunt = c.fetchone()[0]
            print(f"    - Registros totales: {total} | Spam: {spam} | IssueHunt: {issuehunt}")
            
            # Purgar spam en esta BD
            c.execute("DELETE FROM bounty_opportunities WHERE title LIKE '%bounty-plaza%' OR title LIKE '%$999999999%' OR repo LIKE '%bounty-plaza%'")
            deleted = c.rowcount
            conn.commit()
            print(f"    - 🧹 Spam purgado en {os.path.basename(db)}: {deleted} registros eliminados")
        conn.close()
    except Exception as e:
        print(f"    - ⚠️ Error leyendo {db}: {e}")

print("\n==================================================================")
print(" 🛠️ UNIFICANDO RUTAS DE DB EN EL CÓDIGO FUENTE")
print("==================================================================")

files_to_fix = [
    os.path.join(WORKSPACE, "ccia_mando_63.py"),
    os.path.join(WORKSPACE, "modules", "art_63.py"),
    os.path.join(WORKSPACE, "upgrade_bounty_scraper.py"),
    os.path.join(WORKSPACE, "github_outbound_publisher.py")
]

for fpath in files_to_fix:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Forzar el uso de /home/k1/ccia_workspace/ccia_bounties.db
        new_content = re.sub(
            r'DB_PATH\s*=\s*["\'].*?["\']',
            f'DB_PATH = "{CANONICAL_DB}"',
            content
        )
        new_content = re.sub(
            r'db_path\s*=\s*["\'].*?["\']',
            f'db_path = "{CANONICAL_DB}"',
            new_content
        )
        
        if content != new_content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Ruta unificada en: {os.path.basename(fpath)}")
        else:
            print(f"  ℹ️ {os.path.basename(fpath)} ya apuntaba a la ruta canónica.")

print("==================================================================")
print("🚀 SANEAMIENTO COMPLETO: Vuelve a abrir la opción [4] -> [A] en el menú.")
print("==================================================================")
