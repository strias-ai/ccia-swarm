import sqlite3
import json
import urllib.request

DB_PATH = "/home/k1/ccia_workspace/university.db"

def fetch_algora_bounties():
    url = "https://backend.algora.io/api/bounties?status=open"
    req = urllib.request.Request(url, headers={"User-Agent": "CCIA-Agent/17.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return [{"repo": b.get("repository"), "amount": b.get("amount"), "source": "algora"} for b in data if b.get("amount", 0) >= 50]
    except Exception:
        return []

if __name__ == "__main__":
    bounties = fetch_algora_bounties()
    print(f"🎯 Bounties descubiertos en Algora: {len(bounties)}")
