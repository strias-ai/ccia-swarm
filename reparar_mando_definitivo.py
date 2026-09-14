import os
import py_compile
import sqlite3
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")

print("==================================================================")
print(" 🛠️ REPARACIÓN ESTRUCTURAL DE CCIA_MANDO_63.PY")
print("==================================================================")

if os.path.exists(MANDO_PATH):
    with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Reemplazo seguro de la sección del submenú de bounties (Opción 4)
    # Reconstruye la estructura if / elif / else para sub_opt
    sub_menu_clean = '''            sub_opt = input("Submenú > ").strip().lower()
            if sub_opt == "a":
                print("📋 Consultando bounties registrados en la base de datos...")
                try:
                    conn = sqlite3.connect(DB_PATH, timeout=10.0)
                    c = conn.cursor()
                    c.execute("SELECT id, repo, title, issue_id FROM bounty_opportunities WHERE repo NOT LIKE '%bounty-plaza%' AND title NOT LIKE '%bounty-plaza%' ORDER BY id DESC LIMIT 20")
                    rows = c.fetchall()
                    conn.close()
                    if not rows:
                        print("  ℹ️ No hay bounties registrados.")
                    else:
                        for idx, r in enumerate(rows, 1):
                            print(f"  {idx}. {r[1]}#{r[3] or '?'} - {r[2]}")
                except Exception as e:
                    print(f"⚠️ Error al leer BD: {e}")
            elif sub_opt == "b":
                print("🔍 Ejecutando Ingesta Exclusiva de Bounties desde IssueHunt (API GraphQL)...")
                try:
                    import upgrade_bounty_scraper
                    upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
                except Exception as e:
                    print(f"⚠️ Error al ejecutar el scraper de IssueHunt: {e}")
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
                        print("✅ Bounty registrado manualmente.")
                    except Exception as e:
                        print(f"⚠️ Error guardando bounty: {e}")
'''

    # Localizar y reemplazar la sección conflictiva sub_opt
    pattern = r'sub_opt\s*=\s*input\(["\']Submenú > ["\']\).*?(?=\n\s*(?:elif opt|else:|def |if __name__|\Z))'
    
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, sub_menu_clean.strip(), content, flags=re.DOTALL)
    else:
        # Si el patrón exacto no coincide, corregir sangrados rotos manualmente
        content = content.replace('elif sub_opt == "C":', 'elif sub_opt == "c":')
        content = content.replace('elif sub_opt == "B":', 'elif sub_opt == "b":')
        content = content.replace('elif sub_opt == "A":', 'if sub_opt == "a":')

    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    # Validar compilación
    try:
        py_compile.compile(MANDO_PATH, doraise=True)
        print("🟢 'ccia_mando_63.py' compilado sin errores sintácticos.")
    except py_compile.PyCompileError as e:
        print(f"❌ Error de compilación detectado: {e}")

# Purga final en BD
conn = sqlite3.connect(DB_PATH, timeout=30.0)
c = conn.cursor()
c.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%bounty-plaza%' OR title LIKE '%bounty-plaza%' OR title LIKE '%$999999999%'")
conn.commit()
conn.close()
print("🧹 Purga de registros fantasma completada.")

print("==================================================================")
print("🚀 SANEAMIENTO FINALIZADO: Puedes presionar 4 nuevamente.")
print("==================================================================")
