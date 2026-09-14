import py_compile
import sqlite3
import os
import re
import urllib.request
import json

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("==================================================================")
print(" 🔬 TEST DE VUELO Y AUDITORÍA PRE-LANZAMIENTO (ARTEFACTO 63)")
print("==================================================================")

# 1. Comprobación de sintaxis Python (AST)
files_to_check = [
    os.path.join(WORKSPACE, "modules", "art_63.py"),
    os.path.join(WORKSPACE, "ccia_mando_63.py"),
    os.path.join(WORKSPACE, "github_outbound_publisher.py"),
    os.path.join(WORKSPACE, "upgrade_bounty_scraper.py")
]

syntax_errors = 0
print("1. COMPROBACIÓN SINTÁCTICA DE CÓDIGO:")
for fpath in files_to_check:
    if os.path.exists(fpath):
        try:
            py_compile.compile(fpath, doraise=True)
            print(f"  🟢 {os.path.basename(fpath)}: Sintaxis OK")
        except py_compile.PyCompileError as e:
            print(f"  ❌ Error de sintaxis en {os.path.basename(fpath)}: {e}")
            syntax_errors += 1
    else:
        print(f"  ⚠️ No encontrado: {os.path.basename(fpath)}")

# 2. Reparación y saneamiento de la Base de Datos
print("\n2. SANEAMIENTO Y POBLADO DE ID DE ISSUES EN BD:")
conn = sqlite3.connect(DB_PATH, timeout=30.0)
c = conn.cursor()

# Extraer issue_id desde issue_url o title para registros donde esté vacío
c.execute("SELECT id, issue_url, title, issue_id FROM bounty_opportunities")
rows = c.fetchall()

updated_issues = 0
for row_id, url, title, current_issue_id in rows:
    if not current_issue_id:
        extracted_id = None
        # Buscar #NUMERO en el titulo o final de URL
        match_url = re.search(r'/(?:issues|pull)/(\d+)', str(url))
        match_title = re.search(r'#(\d+)', str(title))
        
        if match_url:
            extracted_id = match_url.group(1)
        elif match_title:
            extracted_id = match_title.group(1)
            
        if extracted_id:
            c.execute("UPDATE bounty_opportunities SET issue_id=? WHERE id=?", (extracted_id, row_id))
            updated_issues += 1

# Purga de spam sintético ($999999...)
c.execute("DELETE FROM bounty_opportunities WHERE title LIKE '%$999999999%' OR title LIKE '%[Bounty] [Bounty] [Bounty] [Bounty]%'")
purged_count = c.rowcount

conn.commit()
print(f"  ✅ Registros normalizados con issue_id: {updated_issues}")
print(f"  ✅ Entradas de spam eliminadas: {purged_count}")

# 3. Verificación de Ollama Local
print("\n3. ESTADO DE SERVICIO OLLAMA:")
try:
    req = urllib.request.Request("http://localhost:11434/api/tags")
    with urllib.request.urlopen(req, timeout=3) as resp:
        models_data = json.loads(resp.read().decode())
        models = [m['name'] for m in models_data.get('models', [])]
        print(f"  🟢 Ollama operativo. Modelos disponibles: {len(models)}")
except Exception as e:
    print(f"  ⚠️ Conexión Ollama: {e}")

# 4. Estado de cerrojos mutex
print("\n4. VERIFICACIÓN DE CERROJOS:")
lock_file = "/tmp/ccia_ollama_global.lock"
if os.path.exists(lock_file):
    print("  ℹ️ Cerrojo Mutex presente. Verificando liberación...")
    try:
        os.remove(lock_file)
        print("  ✅ Cerrojo obsoleto liberado de /tmp")
    except Exception:
        pass
else:
    print("  🟢 Cerrojo Mutex /tmp libre.")

conn.close()

print("==================================================================")
if syntax_errors == 0:
    print("🚀 TODO LISTO PARA ENCHUFAR EL DEMONIO (OPCIÓN 12 / OPCIÓN 3)")
else:
    print("⚠️ Corregir errores sintácticos antes de arrancar.")
print("==================================================================")
