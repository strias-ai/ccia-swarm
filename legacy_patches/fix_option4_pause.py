import os
import py_compile
import re

WORKSPACE = "/home/k1/ccia_workspace"
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("==================================================================")
print(" 🛠️ CORRIGIENDO VISUALIZACIÓN Y PAUSA EN SUBMENÚ OPCIÓN 4")
print("==================================================================")

with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

sub_menu_code = '''            sub_opt = input("Submenú > ").strip().lower()
            if sub_opt == "a":
                print("\n📋 BOUNTIES REGISTRADOS EN BD (CANAL ISSUEHUNT):")
                print("-" * 65)
                try:
                    conn = sqlite3.connect(DB_PATH, timeout=10.0)
                    c = conn.cursor()
                    c.execute("SELECT id, repo, title, issue_id, status FROM bounty_opportunities ORDER BY id DESC LIMIT 20")
                    rows = c.fetchall()
                    conn.close()
                    if not rows:
                        print("  ℹ️ No hay bounties en la base de datos.")
                    else:
                        for idx, r in enumerate(rows, 1):
                            print(f"  {idx:2d}. [{r[4]}] {r[1]}#{r[3] or '?'} - {r[2][:55]}")
                except Exception as e:
                    print(f"⚠️ Error al leer BD: {e}")
                input("\n[Presione ENTER para continuar...]")
            elif sub_opt == "b":
                print("\n🔍 INICIANDO SCRAPER EXCLUSIVO ISSUEHUNT (GRAPHQL)...")
                print("-" * 65)
                try:
                    import upgrade_bounty_scraper
                    upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
                except Exception as e:
                    print(f"⚠️ Error al ejecutar scraper: {e}")
                input("\n[Presione ENTER para continuar...]")
            elif sub_opt == "c":
                url = input("Ingrese URL del Issue/Bounty: ").strip()
                title = input("Ingrese Título/Descripción: ").strip()
                if url and title:
                    try:
                        conn = sqlite3.connect(DB_PATH, timeout=10.0)
                        c = conn.cursor()
                        issue_id = url.rstrip("/").split("/")[-1] if "/issues/" in url or "/pull/" in url else None
                        c.execute("INSERT INTO bounty_opportunities (issue_url, repo, title, status, issue_id) VALUES (?, 'Manual', ?, 'PENDING', ?)", (url, title, issue_id))
                        conn.commit()
                        conn.close()
                        print("✅ Bounty registrado correctamente.")
                    except Exception as e:
                        print(f"⚠️ Error guardando bounty: {e}")
                input("\n[Presione ENTER para continuar...]")
'''

pattern = r'sub_opt\s*=\s*input\(["\']Submenú > ["\']\).*?(?=\n\s*(?:elif opt|else:|def |if __name__|\Z))'
if re.search(pattern, content, flags=re.DOTALL):
    content = re.sub(pattern, sub_menu_code.strip(), content, flags=re.DOTALL)
    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✅ Pausas inyectadas en las opciones A, B y C del submenú.")

py_compile.compile(MANDO_PATH, doraise=True)
print("  🟢 Sintaxis de 'ccia_mando_63.py' verificada correctamente.")
print("==================================================================")
