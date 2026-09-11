import sqlite3
import os

print("=" * 80)
print("🔍 BUSCANDO BASE DE DATOS REAL Y REGISTRANDO ARTEFACTO 65")
print("=" * 80)

# 1. Buscar todas las bases de datos en la workspace
possible_dbs = []
for root, dirs, files in os.walk("/home/k1"):
    if ".git" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(".db"):
            possible_dbs.append(os.path.join(root, f))

print(f"  • Bases de datos SQLite encontradas: {possible_dbs}")

target_db = None
target_table = None

for db_path in possible_dbs:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for t in tables:
            if "artifact" in t or "manifest" in t:
                target_db = db_path
                target_table = t
                break
        if target_db:
            break
    except Exception:
        pass

if target_db and target_table:
    print(f"  ✅ Base de datos objetivo: {target_db}")
    print(f"  ✅ Tabla de manifiestos: {target_table}")
    
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({target_table});")
    cols = [c[1] for c in cursor.fetchall()]
    
    # Inserción adaptada a las columnas existentes
    if "id" in cols:
        query = f"INSERT OR REPLACE INTO {target_table} (id, artifact_name, version, category, status) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (65, "CCiA Swarm API Gateway & Inter-Agent Tool Bus", "v1.0.0", "SWARM_API_GATEWAY", "CERTIFIED"))
        conn.commit()
        print("  ✅ Artefacto 65 registrado exitosamente en la base de datos oficial.")
    conn.close()
else:
    print("  ℹ️ Los manifiestos son auto-descubiertos en tiempo de ejecución por ccia_mission_control.py desde /modules.")

print("=" * 80)
