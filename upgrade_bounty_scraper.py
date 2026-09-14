import os
import sqlite3
import urllib.request
import json
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
ENV_PATH = os.path.join(WORKSPACE, ".env")

# Cargar GitHub Token si existe
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
if not GITHUB_TOKEN and os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                GITHUB_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")

def fetch_issuehunt_bounties_exclusive():
    print("==================================================================")
    print(" 🎯 SCRAPER EVOLUTIVO DE BOUNTIES (IssueHunt + GitHub Search API)")
    print("==================================================================")
    
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    c = conn.cursor()
    inserted = 0
    skipped = 0

    candidates = []

    # Fuente 1: GitHub Search API (Búsqueda global de Issues con etiqueta / palabra Bounty)
    print("  🔍 Buscando Bounties activos en repositorios vía GitHub API...")
    search_queries = [
        "is:issue is:open label:bounty",
        "is:issue is:open label:\"help wanted\" bounty",
        "is:issue is:open \"issuehunt\""
    ]

    for q in search_queries:
        try:
            url = f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&sort=created&order=desc&per_page=15"
            headers = {
                "User-Agent": "CCiA-Swarm/1.0",
                "Accept": "application/vnd.github.v3+json"
            }
            if GITHUB_TOKEN:
                headers["Authorization"] = f"token {GITHUB_TOKEN}"

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("items", []):
                    issue_url = item.get("html_url", "")
                    title = item.get("title", "")
                    repo_url = item.get("repository_url", "")
                    repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else "GitHub"
                    issue_id = str(item.get("number", ""))

                    candidates.append({
                        "url": issue_url,
                        "repo": repo_name,
                        "title": title,
                        "issue_id": issue_id
                    })
        except Exception as e:
            print(f"  ⚠️ Error en búsqueda API ({q[:20]}...): {e}")

    # Fuente 2: Scraping de respaldo IssueHunt / Polar.sh público
    print("  🌐 Escaneando directorios públicos de bounties...")
    public_sources = [
        "https://raw.githubusercontent.com/bounty-sources/list/main/bounties.json"
    ]
    for src in public_sources:
        try:
            req = urllib.request.Request(src, headers={"User-Agent": "CCiA-Swarm/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for b in data:
                    candidates.append({
                        "url": b.get("url") or b.get("issue_url"),
                        "repo": b.get("repo", "External"),
                        "title": b.get("title", "Bounty Opportunity"),
                        "issue_id": str(b.get("issue_id", ""))
                    })
        except Exception:
            pass

    # Insertar en base de datos
    for item in candidates:
        url = item.get("url")
        repo = item.get("repo", "Unknown")
        title = item.get("title", "Bounty Issue")
        issue_id = item.get("issue_id")

        if not url:
            continue

        if "bounty-plaza" in repo.lower() or "bounty-plaza" in title.lower():
            continue

        try:
            c.execute("""
                INSERT INTO bounty_opportunities (issue_url, repo, title, status, issue_id)
                VALUES (?, ?, ?, 'PENDING', ?)
            """, (url, repo, title, issue_id))
            inserted += 1
            print(f"  🟢 Añadido: {repo}#{issue_id} -> {title[:50]}")
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()

    print("------------------------------------------------------------------")
    print(f"✅ Ingesta finalizada: {inserted} nuevos bounties registrados | {skipped} existentes.")
    print("==================================================================")

if __name__ == "__main__":
    fetch_issuehunt_bounties_exclusive()
