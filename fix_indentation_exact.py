import py_compile
import re
import os

MANDO_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(MANDO_PATH, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for idx, line in enumerate(lines):
    if re.search(r'elif\s+opt(?:\.strip\(\))?\s*==\s*["\']4["\']\s*:', line):
        start_idx = idx
        break

if start_idx is not None:
    indent_len = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    ind = " " * indent_len
    ind4 = " " * (indent_len + 4)
    ind8 = " " * (indent_len + 8)
    ind12 = " " * (indent_len + 12)

    for idx in range(start_idx + 1, len(lines)):
        line = lines[idx]
        if line.strip() and not line.startswith(" " * (indent_len + 1)):
            if line.lstrip().startswith("elif ") or line.lstrip().startswith("else:") or line.lstrip().startswith("def "):
                end_idx = idx
                break

    if end_idx is not None:
        new_block = [
            f'{ind}elif opt == "4":\n',
            f'{ind4}print("\\n🎯 SUBMENÚ Y BUSCADOR EVOLUTIVO DE BOUNTIES (ISSUEHUNT EXCLUSIVO):")\n',
            f'{ind4}print("  [A] Ver Bounties Registrados en DB")\n',
            f'{ind4}print("  [B] Ejecutar Buscador Evolutivo (IssueHunt API)")\n',
            f'{ind4}print("  [C] Añadir Bounty Manualmente")\n',
            f'{ind4}sub_opt = input("Submenú > ").strip().lower()\n',
            f'{ind4}if sub_opt == "a":\n',
            f'{ind8}print("\\n📋 BOUNTIES REGISTRADOS EN BD (ISSUEHUNT):")\n',
            f'{ind8}print("-" * 65)\n',
            f'{ind8}try:\n',
            f'{ind12}import sqlite3\n',
            f'{ind12}conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)\n',
            f'{ind12}c = conn.cursor()\n',
            f'{ind12}c.execute("SELECT id, repo, title, issue_id, status FROM bounty_opportunities WHERE repo NOT LIKE \'%bounty-plaza%\' AND title NOT LIKE \'%bounty-plaza%\' ORDER BY id DESC LIMIT 20")\n',
            f'{ind12}rows = c.fetchall()\n',
            f'{ind12}conn.close()\n',
            f'{ind12}if not rows:\n',
            f'{ind12}    print("  ℹ️ No hay bounties registrados en la base de datos.")\n',
            f'{ind12}else:\n',
            f'{ind12}    for idx_b, r in enumerate(rows, 1):\n',
            f'{ind12}        print(f"  {{idx_b:2d}}. [{{r[4]}}] {{r[1]}}#{{r[3] or \'?\'}} - {{r[2][:55]}}")\n',
            f'{ind8}except Exception as e:\n',
            f'{ind12}print(f"⚠️ Error al leer BD: {{e}}")\n',
            f'{ind8}input("\\n[Presione ENTER para continuar...]")\n',
            f'{ind4}elif sub_opt == "b":\n',
            f'{ind8}print("\\n🔍 INICIANDO SCRAPER EXCLUSIVO ISSUEHUNT (GRAPHQL API)...")\n',
            f'{ind8}print("-" * 65)\n',
            f'{ind8}try:\n',
            f'{ind12}import upgrade_bounty_scraper\n',
            f'{ind12}upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()\n',
            f'{ind8}except Exception as e:\n',
            f'{ind12}print(f"⚠️ Error al ejecutar scraper: {{e}}")\n',
            f'{ind8}input("\\n[Presione ENTER para continuar...]")\n',
            f'{ind4}elif sub_opt == "c":\n',
            f'{ind8}url = input("Ingrese URL del Issue/Bounty: ").strip()\n',
            f'{ind8}title = input("Ingrese Título/Descripción: ").strip()\n',
            f'{ind8}if url and title:\n',
            f'{ind12}try:\n',
            f'{ind12}    import sqlite3\n',
            f'{ind12}    conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db", timeout=10.0)\n',
            f'{ind12}    c = conn.cursor()\n',
            f'{ind12}    issue_id = url.rstrip("/").split("/")[-1] if "/issues/" in url or "/pull/" in url else None\n',
            f'{ind12}    c.execute("INSERT INTO bounty_opportunities (issue_url, repo, title, status, issue_id) VALUES (?, \'Manual\', ?, \'PENDING\', ?)", (url, title, issue_id))\n',
            f'{ind12}    conn.commit()\n',
            f'{ind12}    conn.close()\n',
            f'{ind12}    print("✅ Bounty registrado correctamente.")\n',
            f'{ind12}except Exception as e:\n',
            f'{ind12}    print(f"⚠️ Error guardando bounty: {{e}}")\n',
            f'{ind8}input("\\n[Presione ENTER para continuar...]")\n',
        ]

        lines[start_idx:end_idx] = new_block

        with open(MANDO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)

        py_compile.compile(MANDO_PATH, doraise=True)
        print("🟢 'ccia_mando_63.py' ajustado con indentación perfecta y validado sin errores de sintaxis.")
    else:
        print("⚠️ No se encontró el final del bloque de la opción 4.")
else:
    print("⚠️ No se encontró la cabecera 'elif opt == 4'.")
