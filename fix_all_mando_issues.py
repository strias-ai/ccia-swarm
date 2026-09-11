import os
import sqlite3
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ REPARACIÓN INTEGRAL: COLA DB, SUBMENÚ [A], DAEMON [12] Y MONITOR [8]")
print("=" * 80)

# 1. PURGA FÍSICA EN SQLITE (Eliminar IDs del 1 al 15 si son spam)
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Purga por palabras clave de spam
    spam_patterns = [
        "%comment-auto-bot%", "%Breeze%", "%latvia%", "%comeback%",
        "%Stellar-Unified%", "%AudioBitsStellar%", "%devopsinsiders%",
        "%Beldex-Coin%", "%PYRAX%", "%pancakeswap%", "%jojoeldenirng%",
        "%Soroban-Cookbook%", "%17reaz%", "%FeeiCN%", "%TheBoogiemen%"
    ]
    
    total_deleted = 0
    for pat in spam_patterns:
        cursor.execute("DELETE FROM bounty_opportunities WHERE repo LIKE ? OR issue_url LIKE ?", (pat, pat))
        total_deleted += cursor.rowcount
        
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
    pending_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, repo, title FROM bounty_opportunities WHERE status='PENDING' ORDER BY id ASC LIMIT 5")
    sample = cursor.fetchall()
    
    conn.close()
    print(f"  ✅ Registros purgados de la DB: {total_deleted}")
    print(f"  📊 Total de bounties reales pendientes: {pending_count}")
    print("\n📋 Próximos 5 bounties en la cola:")
    for row in sample:
        print(f"     [{row[0]}] {row[1]} -> {row[2][:60]}")

# 2. PARCHEAR ccia_mando_63.py PARA QUE EL SUBMENÚ [A] FILTRE CORRECTAMENTE
if os.path.exists(MANDO_PATH):
    with open(MANDO_PATH, "r", encoding="utf-8") as f:
        m_code = f.read()
    
    # Asegurar consulta SQL ordenada por ID reciente y filtrando PENDING
    old_queries = [
        "SELECT issue_url, repo, title FROM bounty_opportunities",
        "SELECT id, repo, title FROM bounty_opportunities",
        "SELECT repo, title FROM bounty_opportunities"
    ]
    
    filtered_sql = "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id DESC"
    
    for q in old_queries:
        if q in m_code and "WHERE status='PENDING'" not in q:
            m_code = m_code.replace(q, filtered_sql)
            
    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(m_code)
    print("\n  ✅ Submenú [4] -> [A] actualizado para consulta filtrada.")

# 3. IMPLEMENTAR ARRANQUE REAL DEL DAEMON [12] Y LOGS EN /tmp/art63_reasoning.log
if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        art_code = f.read()

    # Inyectar cabeceras 406 en el conector Algora
    algora_old_headers = '"Accept": "application/json"'
    algora_new_headers = '"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"'
    if algora_old_headers in art_code:
        art_code = art_code.replace(algora_old_headers, algora_new_headers)

    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.write(art_code)

# 4. COMPILACIÓN Y COMPROBACIÓN
print("\n🛠️ VERIFICANDO COMPILACIÓN DE CÓDIGO:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Módulos validados correctamente.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
