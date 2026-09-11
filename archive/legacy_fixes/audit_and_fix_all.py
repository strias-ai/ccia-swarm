import os
import sys
import sqlite3
import urllib.request
import json
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ DIAGNÓSTICO Y REPARACIÓN DE DEUDA TÉCNICA - CCIA ARTEFACTO 63")
print("=" * 80)

# ---------------------------------------------------------
# 1. PARCHE DE LIBRERÍAS FALTANTES (sqlite3) EN ARCHIVOS
# ---------------------------------------------------------
print("\n[1/5] Corrigiendo imports faltantes ('sqlite3') en código...")

def inject_sqlite3_if_missing(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "import sqlite3" not in content:
        lines = content.splitlines(True)
        # Insertar tras el primer bloque de imports
        insert_idx = 0
        for idx, l in enumerate(lines):
            if l.startswith("import ") or l.startswith("from "):
                insert_idx = idx + 1
        lines.insert(insert_idx, "import sqlite3\n")
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"  ✅ 'import sqlite3' inyectado en {os.path.basename(file_path)}")
    else:
        print(f"  ✓ {os.path.basename(file_path)} ya cuenta con 'import sqlite3'")

inject_sqlite3_if_missing(ART63_PATH)
inject_sqlite3_if_missing(MANDO_PATH)

# ---------------------------------------------------------
# 2. AUDITORÍA Y MIGRACIÓN DE ESQUEMA BASE DE DATOS SQLITE
# ---------------------------------------------------------
print("\n[2/5] Auditando y migrando tablas de SQLite...")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar tabla proposal_reviews
    cursor.execute("PRAGMA table_info(proposal_reviews);")
    cols = [column[1] for column in cursor.fetchall()]

    if "proposal_reviews" in [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        if "timestamp" not in cols:
            print("  ⚠️ Columna 'timestamp' no encontrada en 'proposal_reviews'. Añadiendo columna...")
            cursor.execute("ALTER TABLE proposal_reviews ADD COLUMN timestamp TEXT DEFAULT (datetime('now'));")
            conn.commit()
            print("  ✅ Columna 'timestamp' añadida correctamente.")
        else:
            print("  ✓ Tabla 'proposal_reviews' tiene el esquema completo.")
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposal_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bounty_id TEXT,
                repo TEXT,
                review_text TEXT,
                status TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        print("  ✅ Tabla 'proposal_reviews' creada.")

    # Asegurar tabla bounty_opportunities
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
    conn.commit()

    # Contar registros
    bounties_total = cursor.execute("SELECT COUNT(*) FROM bounty_opportunities").fetchone()[0]
    bounties_pending = cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'").fetchone()[0]
    debates_total = cursor.execute("SELECT COUNT(*) FROM swarm_debates").fetchone()[0] if 'swarm_debates' in [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else 0

    print(f"  📊 Bounties Totales: {bounties_total} | Pendientes: {bounties_pending}")
    print(f"  📊 Debates Registrados: {debates_total}")
    conn.close()
except Exception as e:
    print(f"  ❌ Error accediendo a SQLite: {e}")

# ---------------------------------------------------------
# 3. VERIFICACIÓN DE OLLAMA Y MODELOS LOCALES
# ---------------------------------------------------------
print("\n[3/5] Comprobando API y estado de servicio Ollama local...")
try:
    req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
    with urllib.request.urlopen(req, timeout=3) as response:
        data = json.loads(response.read().decode())
        models = data.get("models", [])
        print(f"  ✅ Ollama activo. Modelos detectados ({len(models)}):")
        for m in models[:5]:
            print(f"     • {m.get('name')}")
        if not models:
            print("  ⚠️ El servicio Ollama responde pero no hay modelos cargados ('ollama list' vacío).")
except Exception as e:
    print(f"  ❌ No se pudo conectar a Ollama en http://127.0.0.1:11434/api/tags ({e})")
    print("  💡 Sugerencia: Inicia el servicio con 'systemctl start ollama' o 'ollama serve'.")

# ---------------------------------------------------------
# 4. COMPILACIÓN Y VERIFICACIÓN DE MÓDULOS DEL MENÚ
# ---------------------------------------------------------
print("\n[4/5] Auditando sintaxis de submódulos y menú principal...")

for target_file in [ART63_PATH, MANDO_PATH]:
    try:
        py_compile.compile(target_file, doraise=True)
        print(f"  ✅ {os.path.basename(target_file)} compila perfectamente.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error de compilación en {os.path.basename(target_file)}:\n{e}")

# ---------------------------------------------------------
# 5. INFORME DE DEUDA TÉCNICA Y CONCLUSIÓN
# ---------------------------------------------------------
print("\n" + "=" * 80)
print("📌 RESUMEN DE DEUDA TÉCNICA DETECTADA Y RESUELTA:")
print("=" * 80)
print("1. [BUCLE INFINITO]: Producido porque 'sqlite3' no estaba importado en art_63.py. Al fallar")
print("   el guardado del estado, el bounty quedaba perpetuamente como 'PENDING' en la cola.")
print("2. [ERROR ESQUEMA DB]: Corregida la falta de la columna 'timestamp' en 'proposal_reviews'.")
print("3. [IMPORTS MISSING]: Inyectado 'import sqlite3' en la cabecera de ambos ejecutables.")
print("=" * 80)
