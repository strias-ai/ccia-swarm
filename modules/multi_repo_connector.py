import urllib.request
import json
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def discover_target_repos(query="topic:security-tools stars:>50"):
    """Descubre y registra repositorios candidatos de forma masiva."""
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=updated&order=desc&per_page=10"
    req = urllib.request.Request(url, headers={"User-Agent": "CCIA-GalaxyScanner/1.0"})
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            items = data.get("items", [])
            print(f"🌌 Repositorios catalogados en el sector: {len(items)}")
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            for repo in items:
                name = repo["full_name"]
                stars = repo["stargazers_count"]
                cursor.execute("""
                    INSERT INTO bounties (repo_name, bounty_amount, status, created_at)
                    VALUES (?, 0.0, 'DISCOVERED', datetime('now'))
                """, (f"github:{name}",))
                print(f"  ⭐ [{stars} stars] {name}")
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"⚠️ Error en exploración: {e}")

if __name__ == "__main__":
    discover_target_repos()
