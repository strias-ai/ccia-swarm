import sqlite3
import urllib.request
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def check_github_pr(repo, pr_number=1):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    req = urllib.request.Request(url, headers={"User-Agent": "CCIA-Bot"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return "CLAIMED" if data.get("merged") else "PR_SUBMITTED"
    except Exception:
        return "PR_SUBMITTED"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT repo_name FROM bounties WHERE status='PR_SUBMITTED'")
repos = cursor.fetchall()

for (repo,) in repos:
    new_status = check_github_pr(repo)
    if new_status == "CLAIMED":
        cursor.execute("UPDATE bounties SET status='CLAIMED' WHERE repo_name=?", (repo,))
        print(f"🟢 Bounty en {repo} cobrado exitosamente.")

conn.commit()
conn.close()
