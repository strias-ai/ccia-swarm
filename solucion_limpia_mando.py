import py_compile
import re
import os

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

handler_code = '''
def handle_option_4_bounties():
    print("\\n🎯 SUBMENÚ Y BUSCADOR EVOLUTIVO DE BOUNTIES (ISSUEHUNT EXCLUSIVO):")
    print("  [A] Ver Bounties Registrados en DB")
    print("  [B] Ejecutar Buscador Evolutivo (IssueHunt API)")
    print("  [C] Añadir Bounty Manualmente")
    sub_opt = input("Submenú > ").strip().lower()
    if sub_opt == "a":
        print("\\n📋 BOUNTIES REGISTRADOS EN BD (ISSUEHUNT):")
        print("-" * 65)
        try:
            import sqlite3
            conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)
            c = conn.cursor()
            c.execute("SELECT id, repo, title, issue_id, status FROM bounty_opportunities WHERE repo NOT LIKE '%bounty-plaza%' AND title NOT LIKE '%bounty-plaza%' ORDER BY id DESC LIMIT 20")
            rows = c.fetchall()
            conn.close()
            if not rows:
                print("  ℹ️ No hay bounties registrados en la base de datos.")
            else:
                for idx, r in enumerate(rows, 1):
                    print(f"  {idx:2d}. [{r[4]}] {r[1]}#{r[3] or '?'} - {r[2][:55]}")
        except Exception as e:
            print(f"⚠️ Error al leer BD: {e}")
        input("\\n[Presione ENTER para continuar...]")
    elif sub_opt == "b":
        print("\\n🔍 INICIANDO SCRAPER EXCLUSIVO ISSUEHUNT (GRAPHQL API)...")
        print("-" * 65)
        try:
            import upgrade_bounty_scraper
            upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
        except Exception as e:
            print(f"⚠️ Error al ejecutar scraper: {e}")
        input("\\n[Presione ENTER para continuar...]")
    elif sub_opt == "c":
        url = input("Ingrese URL del Issue/Bounty: ").strip()
        title = input("Ingrese Título/Descripción: ").strip()
        if url and title:
            try:
                import sqlite3
                conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)
                c = conn.cursor()
                issue_id = url.rstrip("/").split("/")[-1] if "/issues/" in url or "/pull/" in url else None
                c.execute("INSERT INTO bounty_opportunities (issue_url, repo, title, status, issue_id) VALUES (?, 'Manual', ?, 'PENDING', ?)", (url, title, issue_id))
                conn.commit()
                conn.close()
                print("✅ Bounty registrado correctamente.")
            except Exception as e:
                print(f"⚠️ Error guardando bounty: {e}")
        input("\\n[Presione ENTER para continuar...]")
'''

if "def handle_option_4_bounties():" not in code:
    code = handler_code + "\n\n" + code

pattern = r'elif\s+opt(?:\.strip\(\))?\s*==\s*["\']4["\']\s*:.*?(?=\n\s*elif\s+opt|\n\s*else:|\n\s*def |\Z)'
replacement = 'elif opt == "4":\n        handle_option_4_bounties()'

code = re.sub(pattern, replacement, code, flags=re.DOTALL)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(MANDO_PATH, doraise=True)
print("🟢 'ccia_mando_63.py' reparado limpiamente y validado sin errores.")
