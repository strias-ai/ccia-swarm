import sqlite3
import os
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
SCRAPER_PATH = os.path.join(WORKSPACE, "upgrade_bounty_scraper.py")
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")

print("==================================================================")
print(" 🎯 CONFIGURACIÓN EXCLUSIVA DE INGESTA ISSUEHUNT (ANTI-SPAM)")
print("==================================================================")

# 1. Purga total de spam y bounties que no son de IssueHunt
conn = sqlite3.connect(DB_PATH, timeout=30.0)
c = conn.cursor()

c.execute("""
    DELETE FROM bounty_opportunities 
    WHERE repo LIKE '%bounty-plaza%' 
       OR title LIKE '%bounty-plaza%' 
       OR title LIKE '%$999999999%' 
       OR repo LIKE '%OmniBlocks%' 
       OR repo LIKE '%stellar-forge%'
       OR issue_url NOT LIKE '%issuehunt%'
""")
deleted_count = c.rowcount
conn.commit()
print(f"🧹 Purga ejecutada: {deleted_count} registros de spam/GitHub desactivados.")

c.execute("SELECT COUNT(*) FROM bounty_opportunities")
total_remaining = c.fetchone()[0]
print(f"📊 Bounties activos y limpios en BD: {total_remaining}")
conn.close()

# 2. Reescribir upgrade_bounty_scraper.py para consultar ÚNICAMENTE IssueHunt
issuehunt_scraper_code = '''import os
import sqlite3
import urllib.request
import json

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
ENV_PATH = os.path.join(WORKSPACE, ".env")

# Obtener token
ISSUEHUNT_TOKEN = os.getenv("ISSUEHUNT_TOKEN", "")
if not ISSUEHUNT_TOKEN and os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ISSUEHUNT_TOKEN="):
                ISSUEHUNT_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")

if not ISSUEHUNT_TOKEN:
    ISSUEHUNT_TOKEN = "api_27710be0855bff9b2fd7d0bbf1e49bac6d45bbd7cbe1d60aefcec5b0df204979"

def fetch_issuehunt_bounties_exclusive():
    print("==================================================================")
    print(" 🎯 SCRAPER EXCLUSIVO ISSUEHUNT API (GraphQL)")
    print("==================================================================")
    
    headers = {
        "User-Agent": "CCiA-Swarm/1.0",
        "Authorization": f"Bearer {ISSUEHUNT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    url = "https://issuehunt.io/graphql"
    query = """
    query {
      bounties(first: 30, state: OPEN) {
        nodes {
          id
          title
          amount
          currency
          issueUrl
          repository {
            owner
            name
          }
        }
      }
    }
    """

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    c = conn.cursor()

    inserted = 0
    skipped = 0

    try:
        data_payload = json.dumps({"query": query}).encode("utf-8")
        req = urllib.request.Request(url, data=data_payload, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=12) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            bounties = res_json.get("data", {}).get("bounties", {}).get("nodes", [])

            for b in bounties:
                issue_url = b.get("issueUrl") or ""
                repo_owner = b.get("repository", {}).get("owner", "")
                repo_name = b.get("repository", {}).get("name", "")
                repo = f"{repo_owner}/{repo_name}".strip("/") if repo_owner else "IssueHunt"
                amount = b.get("amount", 0)
                currency = b.get("currency", "USD")
                raw_title = b.get("title", "IssueHunt Bounty")
                title = f"[{amount} {currency}] {raw_title}"

                # Extraer issue_id
                issue_id = None
                if "/issues/" in issue_url or "/pull/" in issue_url:
                    issue_id = issue_url.rstrip("/").split("/")[-1]

                # Anti-Spam Blacklist
                if "bounty-plaza" in repo.lower() or "bounty-plaza" in title.lower():
                    continue

                if issue_url:
                    try:
                        c.execute("""
                            INSERT INTO bounty_opportunities (issue_url, repo, title, status, issue_id)
                            VALUES (?, ?, ?, 'PENDING', ?)
                        """, (issue_url, repo, title, issue_id))
                        inserted += 1
                        print(f"  🟢 [IssueHunt] Añadido: {repo} -> {title[:45]}")
                    except sqlite3.IntegrityError:
                        skipped += 1

            conn.commit()
            print("------------------------------------------------------------------")
            print(f"✅ Ingesta finalizada: {inserted} nuevos bounties de IssueHunt | {skipped} existentes.")

    except Exception as e:
        print(f"⚠️ Error al conectar con GraphQL IssueHunt: {e}")

    conn.close()
    print("==================================================================")

if __name__ == "__main__":
    fetch_issuehunt_bounties_exclusive()
'''

with open(SCRAPER_PATH, "w", encoding="utf-8") as f:
    f.write(issuehunt_scraper_code)

print("  ✅ upgrade_bounty_scraper.py reconfigurado para canal exclusivo IssueHunt.")

# 3. Enlazar la Opción B de art_63.py al scraper de IssueHunt
if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        art_code = f.read()

    # Reemplazar la búsqueda genérica en evolutionary_bounty_searcher por la llamada directa
    if "evolutionary_bounty_searcher" in art_code:
        new_searcher = '''    def evolutionary_bounty_searcher(self, keywords=None):
        """Ejecuta únicamente el scraper exclusivo de IssueHunt"""
        import upgrade_bounty_scraper
        upgrade_bounty_scraper.fetch_issuehunt_bounties_exclusive()
'''
        art_code = re.sub(
            r'def evolutionary_bounty_searcher\(self.*?\):.*?(?=\n    def |\Z)',
            new_searcher,
            art_code,
            flags=re.DOTALL
        )
        with open(ART63_PATH, "w", encoding="utf-8") as f:
            f.write(art_code)
        print("  ✅ evolutionary_bounty_searcher en art_63.py reconectado exclusivamente a IssueHunt.")

print("==================================================================")
print("🚀 TODO LISTO: Inicia ahora el buscador desde el menú (4 -> B).")
print("==================================================================")
