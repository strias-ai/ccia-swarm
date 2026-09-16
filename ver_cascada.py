import sqlite3
import re
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "/home/k1/ccia_workspace/ccia_bounties.db"

def clean_think_tags(text):
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'^\s*<think>', '', text)
    return text.strip()

def fetch_github_issue_body(repo, issue_id):
    """Consulta directamente la API/CLI de GitHub apuntando al repositorio remoto especificado."""
    try:
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id), "-R", repo, "--json", "body", "-q", ".body"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def format_block(text, indent="  |       ", max_lines=6):
    text = clean_think_tags(text)
    if not text:
        return f"{indent}(Sin contenido disponible)"
    lines = text.strip().split("\n")
    truncated = lines[:max_lines]
    out = "\n".join(f"{indent}{line}" for line in truncated)
    if len(lines) > max_lines:
        out += f"\n{indent}... [{len(lines) - max_lines} lineas adicionales ocultas]"
    return out

def render_cascade():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(bounty_opportunities)")
    cols = [row[1] for row in cur.fetchall()]
    
    select_cols = ["repo", "issue_id", "title", "status"]
    body_col = "body" if "body" in cols else ("description" if "description" in cols else None)
    
    if body_col:
        select_cols.append(body_col)
    else:
        select_cols.append("''")

    query = f"SELECT {', '.join(select_cols)} FROM bounty_opportunities ORDER BY id DESC LIMIT 10"
    cur.execute(query)
    bounties = cur.fetchall()

    if not bounties:
        print("[!] No hay Bounties registradas en la base de datos.")
        return

    print("\n" + "=" * 80)
    print("  AUDITORIA EN CASCADA (PROBLEMA ORIGINAL VS SOLUCION ENJAMBRE)")
    print("=" * 80 + "\n")

    for item in bounties:
        repo, issue_id, title, status = item[0], item[1], item[2], item[3]
        orig_problem = item[4] if len(item) > 4 and item[4] else None

        # Si no hay cuerpo en SQLite, consultar GitHub remoto con sintaxis "-R repo"
        if not orig_problem or orig_problem.startswith("http") or "Sin cuerpo" in orig_problem:
            remote_body = fetch_github_issue_body(repo, issue_id)
            if remote_body:
                orig_problem = remote_body
            else:
                orig_problem = "Sin cuerpo disponible (Verificar autenticación con 'gh auth status')"

        status_tag = f"[{'OK: SUBMITTED' if status == 'SUBMITTED' else ('FAIL: REJECTED' if status == 'REJECTED' else 'WAIT: PENDING')}]"

        print("+" + "-" * 78)
        print(f"| BOUNTY: {repo}#{issue_id}  {status_tag}")
        print(f"| Titulo: {title}")
        print("+" + "-" * 78)
        
        print("  |-- [0] PROBLEMA ORIGINAL / ISSUE:")
        print(format_block(orig_problem, indent="  |       ", max_lines=4))
        print("  |")

        cur.execute("SELECT content FROM swarm_debates WHERE repo=? AND issue_id=? AND swarm_phase='Fase1' ORDER BY id DESC LIMIT 1", (repo, issue_id))
        f1 = cur.fetchone()
        print("  |-- [1] FASE 1: Diagnostico (Rastreador de Precision)")
        print(format_block(f1[0] if f1 else None, indent="  |       ", max_lines=5))
        print("  |")

        cur.execute("SELECT content FROM swarm_debates WHERE repo=? AND issue_id=? AND swarm_phase='Fase2' ORDER BY id DESC LIMIT 1", (repo, issue_id))
        f2 = cur.fetchone()
        print("  |-- [2] FASE 2: Codigo / Modificacion (Surgical Coder)")
        print(format_block(f2[0] if f2 else None, indent="  |       ", max_lines=5))
        print("  |")

        cur.execute("SELECT score, feedback FROM proposal_reviews WHERE repo=? AND issue_id=? ORDER BY id DESC LIMIT 1", (repo, issue_id))
        f3 = cur.fetchone()
        print("  `-- [3] FASE 3: Evaluacion Reina (Gatekeeper)")
        if f3:
            print(f"          * Puntuacion: {f3[0]}/10\n          * Feedback  : {f3[1]}")
        else:
            print("          (Sin evaluacion de Reina)")

        print("\n")

    conn.close()

if __name__ == "__main__":
    render_cascade()
