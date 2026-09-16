import subprocess
import os
import json
import sqlite3
import shutil

DB_PATH = "/home/k1/ccia_workspace/ccia_bounties.db"

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout, res.stderr

def find_project_root(base_dir, target_file):
    for root, _, files in os.walk(base_dir):
        if target_file in files:
            return root
    return base_dir

def check_local_compilation(repo_dir):
    if os.path.exists(os.path.join(repo_dir, "go.mod")):
        return run_cmd("go test ./...", cwd=repo_dir)
    elif os.path.exists(os.path.join(repo_dir, "package.json")):
        return run_cmd("npm test --if-present", cwd=repo_dir)
    elif os.path.exists(os.path.join(repo_dir, "pytest.ini")) or os.path.exists(os.path.join(repo_dir, "requirements.txt")):
        return run_cmd("pytest", cwd=repo_dir)
    return 0, "Sin runner de tests detectado", ""

def get_prs_from_github():
    # Sintaxis corregida usando headRepository y search
    cmd = "gh search prs --author '@me' --json number,title,repository,url,state"
    code, out, err = run_cmd(cmd)
    if code == 0 and out.strip():
        try:
            return json.loads(out)
        except Exception:
            pass
    return []

def get_bounties_from_db():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT repo, issue_id, title, status FROM bounty_opportunities")
    rows = cur.fetchall()
    conn.close()
    return [{"repo": r[0], "issue_id": r[1], "title": r[2], "status": r[3]} for r in rows]

def main():
    print("🔍 [1/2] Consultando Pull Requests en GitHub...")
    gh_prs = get_prs_from_github()
    print(f"📌 PRs encontrados en GitHub: {len(gh_prs)}")
    for pr in gh_prs:
        repo = pr.get("repository", {}).get("nameWithOwner", "Desconocido")
        print(f"  • PR #{pr.get('number')} en {repo} [{pr.get('state')}]: {pr.get('title')}")

    print("\n🔍 [2/2] Consultando registro interno de Bounties (ccia_bounties.db)...")
    db_bounties = get_bounties_from_db()
    print(f"📌 Bounties registradas localmente: {len(db_bounties)}")
    
    for b in db_bounties:
        print(f"\n--------------------------------------------------")
        print(f"📂 Repo: {b['repo']} | Issue #{b['issue_id']} | Estado: {b['status']}")
        print(f"📝 Titulo: {b['title']}")
        
        work_dir = f"/tmp/audit_bounty_{b['issue_id']}"
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
            
        code, out, err = run_cmd(f"git clone --depth 1 https://github.com/{b['repo']}.git {work_dir}")
        if code == 0:
            real_root = find_project_root(work_dir, "go.mod")
            c_code, c_out, c_err = check_local_compilation(real_root)
            if c_code == 0:
                print("✅ Tests de repositorio base: PASAN")
            else:
                print("❌ Tests de repositorio base: FALLAN (requiere fix especifico)")
                print(c_err[:300] if c_err else c_out[:300])

if __name__ == "__main__":
    main()
