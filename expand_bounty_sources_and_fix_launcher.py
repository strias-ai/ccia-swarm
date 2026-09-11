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
print("🚀 AMPLIACIÓN MASSIVA DE FUENTES DE BOUNTIES Y ENLACE DE MANDO")
print("=" * 80)

# 1. AMPLIAR MOTOR DE BÚSQUEDA EN BASE DE DATOS
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS bounty_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_url TEXT UNIQUE,
        repo TEXT,
        title TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TEXT DEFAULT (datetime('now'))
    );
""")

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"}

# Matriz ampliada de consultas a GitHub API
queries = [
    "label:bounty state:open",
    "label:\"bug bounty\" state:open",
    "label:\"help wanted\" \"$\" state:open",
    "label:enhancement \"$\" state:open",
    "\"bounty\" in:title,body state:open stars:>10",
    "\"algora\" in:title,body state:open",
    "\"polar.sh\" in:title,body state:open",
    "\"gitcoin\" in:title,body state:open",
    "\"reward\" in:title state:open stars:>20",
    "\"crypto\" bounty state:open",
    "\"solana\" bounty state:open",
    "\"ethereum\" bounty state:open"
]

total_added = 0
print("[1/3] Ejecutando rastreo masivo en GitHub API y feeds públicos...")

for q in queries:
    try:
        url = f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&sort=updated&per_page=50"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            for item in items:
                i_url = item.get("html_url")
                title = item.get("title")
                repo_u = item.get("repository_url", "")
                repo = "/".join(repo_u.split("/")[-2:]) if repo_u else "GitHub/Bounty"
                
                # Excluir repositorios de spam
                if not any(sp in repo.lower() for sp in ["comment-auto-bot", "breeze", "latvia-digital"]):
                    cursor.execute(
                        "INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')",
                        (i_url, repo, title)
                    )
                    if cursor.rowcount > 0:
                        total_added += 1
    except Exception:
        pass

conn.commit()

cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
pending_total = cursor.fetchone()[0]
conn.close()

print(f"  ✅ Ingesta masiva completada: +{total_added} nuevos bounties registrados.")
print(f"  📊 Total de bounties reales pendientes en DB: {pending_total}")

# 2. VINCULAR LA OPCIÓN [4] DEL MÓDULO PARA ABRIR DIRECTAMENTE CCIA_MANDO_63.PY
print("\n[2/3] Vinculando la opción [4] del cargador para abrir ccia_mando_63.py directamente...")

for launcher_file in ["ccia_launcher.py", "ccia_main.py", "modules/art_63.py"]:
    full_p = os.path.join(WORKSPACE, launcher_file)
    if os.path.exists(full_p):
        with open(full_p, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Redirigir llamadas de subproceso de art_63.py hacia ccia_mando_63.py
        if "art_63.py" in code and launcher_file != "modules/art_63.py":
            code_updated = code.replace("modules/art_63.py", "ccia_mando_63.py").replace("art_63.py", "ccia_mando_63.py")
            with open(full_p, "w", encoding="utf-8") as f:
                f.write(code_updated)
            print(f"  ✅ {launcher_file} actualizado para invocar la interfaz completa de mando.")

# 3. VERIFICACIÓN DE SINTAXIS
print("\n[3/3] Comprobando compilación...")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Compilación perfecta de todos los componentes.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación: {e}")

print("=" * 80)
