import os
import sqlite3
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")

print("=" * 80)
print("PURGA DEFINITIVA DE SPAM Y PARCHE DE SUBMENÚ EN ARTEFACTO 63")
print("=" * 80)

# 1. PURGA COMPLETA EN BASE DE DATOS SQLITE
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

spam_patterns = [
    "%comment-auto-bot%",
    "%Breeze%",
    "%latvia-digital-resilience%",
    "%comeback%"
]

total_purged = 0
for pattern in spam_patterns:
    cursor.execute("DELETE FROM bounty_opportunities WHERE repo LIKE ? OR issue_url LIKE ?", (pattern, pattern))
    total_purged += cursor.rowcount

conn.commit()

cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
pending_count = cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'").fetchone()[0]
conn.close()

print(f"  ✅ Entradas de spam purgadas: {total_purged}")
print(f"  📊 Bounties pendientes reales en DB: {pending_count}")

# 2. PARCHE EN modules/art_63.py PARA INTEGRAR SCRAPER Y MUESTRA LIMPIA
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Reemplazar o asegurar consulta SQL ordenada por IDs recientes y filtrando PENDING
old_select_query = "SELECT issue_url, repo, title FROM bounty_opportunities"
new_select_query = "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id DESC"

if old_select_query in code:
    code = code.replace(old_select_query, new_select_query)

# Definición del Scraper Reputacional Integrado
scraper_code = '''
def run_evolutionary_scraper(db_path="/home/k1/ccia_workspace/ccia_bounties.db"):
    import urllib.request
    import json
    import sqlite3
    import urllib.parse
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    queries = [
        "label:bounty stars:>100 state:open",
        "label:\\"help wanted\\" \\"$100\\" stars:>200 state:open",
        "algora stars:>100 state:open"
    ]
    
    new_added = 0
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bounty_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_url TEXT UNIQUE,
            repo TEXT,
            title TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    
    for q in queries:
        try:
            url = f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&sort=updated&per_page=15"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("items", []):
                    issue_url = item.get("html_url")
                    title = item.get("title")
                    repo_url = item.get("repository_url", "")
                    repo = "/".join(repo_url.split("/")[-2:]) if repo_url else "GitHub/Bounty"
                    
                    if "comment-auto-bot" not in repo and "Breeze" not in repo:
                        cursor.execute(
                            "INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')",
                            (issue_url, repo, title)
                        )
                        if cursor.rowcount > 0:
                            new_added += 1
        except Exception:
            pass
            
    conn.commit()
    conn.close()
    return new_added
'''

if "def run_evolutionary_scraper" not in code:
    code += "\n\n" + scraper_code

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("\n🛠️ VERIFICACIÓN DE COMPILACIÓN EN ARTEFACTO 63:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: modules/art_63.py actualizado.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
