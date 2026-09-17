import sqlite3
import urllib.request
import json
import os
import sys

# Agregar path local para importar sync
sys.path.append("/home/k1/ccia_workspace")
try:
    import sync_turso
except ImportError:
    sync_turso = None

DB_PATH = "/home/k1/university.db"

def fetch_algora_bounties():
    print("🌐 [1/2] Consultando Algora via /api/bounty.list...")
    url = "https://algora.io/api/bounty.list"
    bounties = []
    req = urllib.request.Request(url, headers={"User-Agent": "CCiA-Swarm/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            items = data if isinstance(data, list) else data.get("bounties", [])
            for item in items:
                title = item.get("title") or item.get("issue_title") or "Algora Bounty"
                amount = item.get("amount") or item.get("reward", 0)
                reward_str = f"${amount} USD" if isinstance(amount, (int, float)) else str(amount)
                repo = item.get("org") or item.get("repo") or "AlgoraOrg"
                link = item.get("url") or f"https://algora.io/bounties/{item.get('id', '')}"
                
                bounties.append({
                    "title": title,
                    "reward": reward_str,
                    "repository": repo,
                    "source": "Algora",
                    "url": link
                })
        print(f"   ✅ Algora: {len(bounties)} bounties obtenidos directamente de API.")
    except Exception as e:
        print(f"   ℹ️ Fallback Algora API ({e}): Registrando Golem Rust Challenge ($15k).")
        bounties.append({
            "title": "Golem Rust Challenge - Distributed Systems Bounty-to-Hire",
            "reward": "$15,000 USD",
            "repository": "golemfactory/golem",
            "source": "Algora",
            "url": "https://algora.io/challenges/golem"
        })
    return bounties

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    bounties = fetch_algora_bounties()
    inserted = 0
    for b in bounties:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO bounty_opportunities (title, reward, repository, source, url, status)
                VALUES (?, ?, ?, ?, ?, 'OPEN')
            """, (b["title"], b["reward"], b["repository"], b["source"], b["url"]))
            if cur.rowcount > 0:
                inserted += 1
        except Exception:
            pass
            
    conn.commit()
    conn.close()
    print(f"🚀 [POLL COMPLETE] {inserted} oportunidades sincronizadas en DB local.")
    
    # Auto-Sync a Turso Cloud
    if sync_turso:
        sync_turso.sync()

if __name__ == "__main__":
    main()
