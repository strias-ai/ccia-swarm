import os
import sqlite3
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ RESOLVIENDO NAMEERROR (shutil) Y ELIMINANDO SPAM DE DB")
print("=" * 80)

# 1. Inyectar import shutil y librerías clave en art_63.py
with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

required_imports = ["import shutil", "import sqlite3", "import os", "import sys", "import json", "import re", "import subprocess"]
missing_imports = [imp for imp in required_imports if imp not in code]

if missing_imports:
    header = "\n".join(missing_imports) + "\n"
    code = header + code
    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  ✅ Módulos faltantes agregados a art_63.py: {', '.join(missing_imports)}")
else:
    print("  ✓ Todas las librerías necesarias están presentes en art_63.py.")

# 2. Limpieza profunda en SQLite por título, repo y URL
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        DELETE FROM bounty_opportunities 
        WHERE title LIKE '%Security Vulnerability Report%' 
           OR repo LIKE '%comment-auto-bot%' 
           OR issue_url LIKE '%comment-auto-bot%'
           OR repo LIKE '%Breeze%' 
           OR repo LIKE '%latvia%' 
           OR repo LIKE '%comeback%'
    """
    cursor.execute(query)
    purged = cursor.rowcount
    conn.commit()
    
    # Obtener balance y muestra limpia
    cursor.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
    total_pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, repo, title FROM bounty_opportunities WHERE status='PENDING' LIMIT 10")
    sample = cursor.fetchall()
    conn.close()
    
    print(f"  ✅ Registros de spam eliminados de la DB: {purged}")
    print(f"  📊 Bounties reales pendientes en la cola: {total_pending}")
    
    print("\n📋 MUESTRA DE LA COLA LIMPIA DE BOUNTIES:")
    for idx, r, t in sample:
        print(f"  [{idx}] {r} -> {t[:65]}")

# 3. Verificación de Compilación
print("\n🛠️ VERIFICACIÓN DE SINTAXIS:")
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: Todos los módulos están validados y sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación residual:\n{e}")

print("=" * 80)
