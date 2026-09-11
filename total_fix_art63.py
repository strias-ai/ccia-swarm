import os
import sqlite3
import re
import py_compile
import urllib.request
import urllib.parse
import json

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ SOLUCIÓN TOTAL: DEPURACIÓN DE CÓDIGO, BASE DE DATOS Y BUCLES")
print("=" * 80)

# 1. PURGA ABSOLUTA DE SPAM Y REPOBLADO EN SQLITE
if os.path.exists(DB_PATH):
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
    deleted = cursor.rowcount
    conn.commit()
    print(f"  ✅ Registros de spam purgados de SQLite: {deleted}")
    
    cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%'")
    pending = cursor.fetchone()[0]
    
    if pending == 0:
        print("  🔍 Buscando nuevos bounties reales para repoblar la base de datos...")
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        query_url = "https://api.github.com/search/issues?q=label:bounty+stars:>100+state:open&sort=updated&per_page=25"
        try:
            req = urllib.request.Request(query_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get("items", []):
                    i_url = item.get("html_url")
                    title = item.get("title")
                    repo_u = item.get("repository_url", "")
                    repo = "/".join(repo_u.split("/")[-2:]) if repo_u else "GitHub/Bounty"
                    if "comment-auto-bot" not in repo and "Breeze" not in repo:
                        cursor.execute(
                            "INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')",
                            (i_url, repo, title)
                        )
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
            pending = cursor.fetchone()[0]
            print(f"  🚀 {pending} bounties de repositorios populares agregados a la DB.")
        except Exception as e:
            print(f"  ⚠️ Error consultando API de GitHub: {e}")
    else:
        print(f"  📊 Bounties válidos activos en cola PENDING: {pending}")
    conn.close()

# 2. CORRECCIÓN Y NORMALIZACIÓN DE IMPORTACIONES EN modules/art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

header_imports = """import os
import sys
import re
import json
import shutil
import sqlite3
import urllib
import urllib.request
import urllib.parse
import subprocess
"""

lines = code.splitlines()
non_import_start = 0
for i, l in enumerate(lines):
    l_str = l.strip()
    if l_str and not l_str.startswith("import ") and not l_str.startswith("from ") and not l_str.startswith("#"):
        non_import_start = i
        break

clean_code_body = "\n".join(lines[non_import_start:])
new_art63 = header_imports + "\n" + clean_code_body

# Forzar filtrado de spam en las consultas internas
new_art63 = new_art63.replace(
    "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING'",
    "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' AND repo NOT LIKE '%Breeze%'"
).replace(
    "SELECT issue_url, repo, title FROM bounty_opportunities",
    "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' AND repo NOT LIKE '%Breeze%'"
)

# Desactivar llamada recursiva al script de mando
if 'subprocess.run([sys.executable, mando_script])' in new_art63:
    new_art63 = new_art63.replace('subprocess.run([sys.executable, mando_script])', '# subprocess.run([sys.executable, mando_script])')

# Inyectar importaciones locales en las funciones de inferencia de Ollama
new_art63 = re.sub(
    r'(def\s+(?:call_ollama|query_ollama|run_model|infer_ollama|ask_ollama|query_model)[^:]*:\n)',
    r'\1    import urllib.request, urllib.parse, json\n',
    new_art63
)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(new_art63)

# 3. NORMALIZACIÓN EN ccia_mando_63.py
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    m_code = f.read()

m_lines = m_code.splitlines()
m_non_import_start = 0
for i, l in enumerate(m_lines):
    l_str = l.strip()
    if l_str and not l_str.startswith("import ") and not l_str.startswith("from ") and not l_str.startswith("#"):
        m_non_import_start = i
        break

m_clean_body = "\n".join(m_lines[m_non_import_start:])
new_mando = header_imports + "\n" + m_clean_body

new_mando = new_mando.replace(
    "SELECT issue_url, repo, title FROM bounty_opportunities",
    "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' AND repo NOT LIKE '%Breeze%'"
).replace(
    "SELECT id, repo, title FROM bounty_opportunities",
    "SELECT id, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' AND repo NOT LIKE '%Breeze%'"
)

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(new_mando)

# 4. RECOMPILACIÓN Y VERIFICACIÓN
print("\n🛠️ RECOMPILACIÓN DE ARCHIVOS:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    print("  ✅ modules/art_63.py verificado y sin errores.")
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ ccia_mando_63.py verificado y sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación residual:\n{e}")

print("=" * 80)
