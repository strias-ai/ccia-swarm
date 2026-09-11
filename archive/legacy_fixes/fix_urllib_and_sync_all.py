import os
import sqlite3
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ REPARACIÓN INTEGRAL: CONECTOR OLLAMA (urllib) Y SINCRONIZACIÓN DB/MENÚ")
print("=" * 80)

# 1. Inyectar importaciones faltantes de urllib en art_63.py y ccia_mando_63.py
imports_to_add = [
    "import urllib",
    "import urllib.request",
    "import urllib.parse",
    "import shutil",
    "import sqlite3",
    "import os",
    "import sys",
    "import json",
    "import re",
    "import subprocess"
]

for file_path in [ART63_PATH, MANDO_PATH]:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        missing = [imp for imp in imports_to_add if imp not in content]
        if missing:
            header = "\n".join(missing) + "\n"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(header + content)
            print(f"  ✅ Importaciones inyectadas en {os.path.basename(file_path)}: {len(missing)}")
        else:
            print(f"  ✓ {os.path.basename(file_path)} tiene todas las importaciones necesarias.")

# 2. Limpieza exhaustiva de spam en la base de datos SQLite
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Eliminar cualquier registro relacionado con spam
    cursor.execute("""
        DELETE FROM bounty_opportunities 
        WHERE repo LIKE '%comment-auto-bot%' 
           OR issue_url LIKE '%comment-auto-bot%'
           OR title LIKE '%Security Vulnerability Report%'
           OR repo LIKE '%Breeze%' 
           OR repo LIKE '%latvia%' 
           OR repo LIKE '%comeback%'
    """)
    purged_count = cursor.rowcount
    conn.commit()
    
    # Asegurar que los bounties válidos tengan estado PENDING
    cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
    pending_real = cursor.fetchone()[0]
    
    conn.close()
    print(f"  ✅ Registros obsoletos eliminados de SQLite: {purged_count}")
    print(f"  📊 Bounties reales en cola activos: {pending_real}")

# 3. Parchear ccia_mando_63.py para que la opción [4] -> [A] consulte exclusivamente bounties limpios
if os.path.exists(MANDO_PATH):
    with open(MANDO_PATH, "r", encoding="utf-8") as f:
        mando_code = f.read()
    
    # Reemplazar consultas SQL genéricas por consultas filtradas
    mando_code_updated = mando_code.replace(
        "SELECT issue_url, repo, title FROM bounty_opportunities",
        "SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC"
    ).replace(
        "SELECT id, repo, title FROM bounty_opportunities",
        "SELECT id, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC"
    )
    
    with open(MANDO_PATH, "w", encoding="utf-8") as f:
        f.write(mando_code_updated)
    print("  ✅ Consultas del menú ccia_mando_63.py sincronizadas con el filtro de reputación.")

# 4. Verificación final de compilación Python
print("\n🛠️ VERIFICACIÓN DE COMPILACIÓN:")
for target in [ART63_PATH, MANDO_PATH]:
    try:
        py_compile.compile(target, doraise=True)
        print(f"  ✅ {os.path.basename(target)} compila correctamente.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error de compilación en {os.path.basename(target)}:\n{e}")

print("=" * 80)
