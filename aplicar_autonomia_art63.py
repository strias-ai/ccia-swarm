import sqlite3
import os
import re

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
ENV_PATH = os.path.join(WORKSPACE, ".env")
ISSUEHUNT_TOKEN = "api_27710be0855bff9b2fd7d0bbf1e49bac6d45bbd7cbe1d60aefcec5b0df204979"

print("==================================================================")
print(" ⚡ UNIFICACIÓN Y AUTONOMÍA COMPLETA ARTEFACTO 63")
print("==================================================================")

# 1. Registrar credencial en .env si no existe
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        env_content = f.read()
else:
    env_content = ""

if "ISSUEHUNT_TOKEN" not in env_content:
    with open(ENV_PATH, "a", encoding="utf-8") as f:
        f.write(f'\nISSUEHUNT_TOKEN="{ISSUEHUNT_TOKEN}"\n')
    print("  ✅ Token de IssueHunt registrado en .env")

# 2. Migrar y homogeneizar esquema SQLite
conn = sqlite3.connect(DB_PATH, timeout=30.0)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bounty_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_url TEXT UNIQUE,
    repo TEXT,
    title TEXT,
    status TEXT DEFAULT 'PENDING',
    issue_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Asegurar columnas faltantes
cursor.execute("PRAGMA table_info(bounty_opportunities);")
existing_cols = [col[1] for col in cursor.fetchall()]
if "issue_id" not in existing_cols:
    cursor.execute("ALTER TABLE bounty_opportunities ADD COLUMN issue_id TEXT;")
    print("  ✅ Columna 'issue_id' añadida a bounty_opportunities")

conn.commit()
conn.close()
print("  ✅ Base de datos ccia_bounties.db sincronizada en modo WAL")

# 3. Inyectar conector IssueHunt y Auto-Buscador en art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Añadir método de auto-renovación si no está implementado
searcher_code = '''
    def auto_refresh_bounties_if_empty(self):
        """Disparador automático: si no hay bounties PENDING, ejecuta el buscador evolutivo e IssueHunt"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
            count = c.fetchone()[0]
            conn.close()
            
            if count == 0:
                print("🔄 [AUTONOMÍA ART63] 0 Bounties pendientes. Activando ingesta automática IssueHunt + GitHub...")
                # Ingesta IssueHunt
                import urllib.request, json
                token = os.getenv("ISSUEHUNT_TOKEN", "")
                if token:
                    req_h = {
                        "User-Agent": "CCiA-Swarm/1.0",
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    query = 'query { bounties(first: 10, state: OPEN) { nodes { issueUrl title repository { owner name } } } }'
                    try:
                        req = urllib.request.Request("https://issuehunt.io/graphql", data=json.dumps({"query": query}).encode(), headers=req_h, method="POST")
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            res = json.loads(resp.read().decode())
                            nodes = res.get("data", {}).get("bounties", {}).get("nodes", [])
                            conn_in = sqlite3.connect(self.db_path, timeout=30.0)
                            c_in = conn_in.cursor()
                            for n in nodes:
                                url = n.get("issueUrl")
                                repo = f"{n.get('repository', {}).get('owner')}/{n.get('repository', {}).get('name')}"
                                title = n.get("title", "IssueHunt Bounty")
                                if url:
                                    c_in.execute("INSERT OR IGNORE INTO bounty_opportunities (issue_url, repo, title, status) VALUES (?, ?, ?, 'PENDING')", (url, repo, title))
                            conn_in.commit()
                            conn_in.close()
                    except Exception as e:
                        print(f"⚠️ Ingesta IssueHunt omitida: {e}")
                
                # Ejecutar Scraper secundario
                os.system("python3 /home/k1/ccia_workspace/upgrade_bounty_scraper.py > /dev/null 2>&1")
        except Exception as ex:
            print(f"⚠️ Error en auto_refresh_bounties_if_empty: {ex}")
'''

if "def auto_refresh_bounties_if_empty" not in code:
    code = code.replace("class TriSwarmOrchestrator:", "class TriSwarmOrchestrator:\n" + searcher_code)
    print("  ✅ Método auto_refresh_bounties_if_empty inyectado en TriSwarmOrchestrator")

# Modificar el bucle del daemon para invocar la renovación y la publicación directa
if "self.auto_refresh_bounties_if_empty()" not in code:
    code = re.sub(
        r'(def run_daemon_loop\(\):.*?\n)',
        r'\1    orchestrator = TriSwarmOrchestrator()\n    orchestrator.auto_refresh_bounties_if_empty()\n',
        code,
        count=1,
        flags=re.DOTALL
    )
    print("  ✅ Disparador de auto-renovación conectado en run_daemon_loop()")

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("------------------------------------------------------------------")
print("🚀 INTEGRACIÓN COMPLETADA: El Artefacto 63 ahora es 100% autónomo.")
print("==================================================================")
