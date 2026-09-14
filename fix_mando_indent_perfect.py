import py_compile
import re
import os

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# 1. Limpiar versiones previas de handle_option_4_bounties si existen
if "def handle_option_4_bounties():" in content:
    content = re.sub(r'def handle_option_4_bounties\(\):.*?(?=\n\s*def |\n\s*class |\n[A-Za-z0-9_]+\s*=|\Z)', '', content, flags=re.DOTALL)

handler_func = '''def handle_option_4_bounties():
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

# 2. Prepend la función y reconstruir líneas
lines = handler_func.splitlines(True) + ["\n"] + content.splitlines(True)
out_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    if re.search(r'elif\s+opt(?:\.strip\(\))?\s*==\s*["\']4["\']\s*:', line):
        indent_len = len(line) - len(line.lstrip())
        indent_str = line[:indent_len]
        body_indent_str = indent_str + "    "
        
        out_lines.append(f"{indent_str}elif opt == \"4\":\n")
        out_lines.append(f"{body_indent_str}handle_option_4_bounties()\n")
        
        i += 1
        while i < len(lines):
            next_line = lines[i]
            if next_line.strip() and (len(next_line) - len(next_line.lstrip()) <= indent_len):
                break
            i += 1
    else:
        out_lines.append(line)
        i += 1

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

py_compile.compile(MANDO_PATH, doraise=True)
print("🟢 'ccia_mando_63.py' reparado limpiamente con sangrado exacto y validado sin errores.")
