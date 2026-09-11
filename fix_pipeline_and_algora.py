import os
import sqlite3
import urllib.request
import urllib.parse
import json
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ DESBLOQUEO DE BUCLE, PURGA DEFINITIVA Y CONECTOR ALGORA / POLAR")
print("=" * 80)

# 1. Purga total de spam y cambio de estado a SKIPPED/COMPLETED
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM bounty_opportunities 
    WHERE repo LIKE '%comment-auto-bot%' 
       OR issue_url LIKE '%comment-auto-bot%'
       OR title LIKE '%Security Vulnerability Report%'
       OR repo LIKE '%Breeze%' 
       OR repo LIKE '%latvia%' 
       OR repo LIKE '%comeback%'
""")
purged_count = cursor.rowcount
conn.commit()
print(f"[1/4] Purgados {purged_count} registros de spam de la base de datos.")

# 2. Ingesta desde Algora API y Polar API
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

added_algora = 0
print("[2/4] Consultando bounties activos en Algora y Polar...")

# Feed de Algora
try:
    req = urllib.request.Request("https://console.algora.io/api/bounties", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        items = data.get("bounties", []) if isinstance(data, dict) else data
        for item in items:
            task = item.get("task", {})
            url = task.get("url") or item.get("url")
            repo = task.get("repo_name") or "algora/bounty"
            amount = item.get("amount", 0)
            currency = item.get("currency", "USD")
            title = f"[{currency} {amount}] " + (task.get("title") or "Algora Issue")
            
            if url and "comment-auto-bot" not in repo:
                cursor.execute(
                    "INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')",
                    (url, repo, title)
                )
                if cursor.rowcount > 0:
                    added_algora += 1
except Exception as e:
    print(f"  ⚠️ Notificación Algora Feed: {e}")

# Feed de GitHub (Bounties reales con recompensas explícitas)
added_github = 0
github_queries = [
    "label:bounty state:open stars:>50",
    "\"algora\" state:open stars:>20",
    "\"polar.sh\" state:open stars:>20",
    "label:\"help wanted\" \"$100\" state:open",
    "label:\"help wanted\" \"$500\" state:open"
]

for gq in github_queries:
    try:
        url = f"https://api.github.com/search/issues?q={urllib.parse.quote(gq)}&sort=updated&per_page=30"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            for item in res_data.get("items", []):
                issue_url = item.get("html_url")
                title = item.get("title")
                repo_url = item.get("repository_url", "")
                repo = "/".join(repo_url.split("/")[-2:]) if repo_url else "GitHub/Bounty"
                
                if not any(sp in repo.lower() for sp in ["comment-auto-bot", "breeze", "latvia"]):
                    cursor.execute(
                        "INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')",
                        (issue_url, repo, title)
                    )
                    if cursor.rowcount > 0:
                        added_github += 1
    except Exception:
        pass

conn.commit()

cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
pending_total = cursor.fetchone()[0]

print(f"  ✅ Nuevos Bounties agregados: Algora ({added_algora}), GitHub/Polar ({added_github}).")
print(f"  📊 Total de bounties listos en cola PENDING: {pending_total}")

# 3. Actualizar art_63.py para marcar bounties como 'PROCESSING' / 'COMPLETED' al tomarlos
print("\n[3/4] Parcheando motor de ejecución para evitar bucles repetitivos...")

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Forzar actualización de estado a COMPLETED en SQLite al procesar
status_update_snippet = """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE bounty_opportunities SET status='COMPLETED' WHERE issue_url=? OR repo=?", (issue_url, repo))
            conn.commit()
            conn.close()
        except Exception:
            pass
"""

if "def process_bounty_loop" in code and "UPDATE bounty_opportunities SET status='COMPLETED'" not in code:
    code = code.replace("def process_bounty_loop(self, issue_url, repo, title=\"\"):", 
                        "def process_bounty_loop(self, issue_url, repo, title=\"\"):\n" + status_update_snippet)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

# 4. Verificación de compilación
print("\n[4/4] Verificando compilación...")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Módulos validados y compilados sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación: {e}")

conn.close()
print("=" * 80)
