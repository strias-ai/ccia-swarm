import os
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

start_marker = 'elif opt == "4":'
if start_marker not in content:
    start_marker = "elif opt == '4':"

if start_marker in content:
    parts = content.split(start_marker, 1)
    before = parts[0]
    rest = parts[1]
    
    next_opt_idx = len(rest)
    for target in ['elif opt == "', "elif opt == '", 'elif opt.strip() == "', 'else:', 'def ']:
        pos = rest.find(target)
        if pos != -1 and pos < next_opt_idx:
            next_opt_idx = pos
            
    after = rest[next_opt_idx:]
    
    option_4_clean = '''elif opt == "4":
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

    new_content = before + option_4_clean + after
    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

py_compile.compile(MANDO_PATH, doraise=True)
print("🟢 Sintaxis de 'ccia_mando_63.py' corregida y verificada exitosamente.")
