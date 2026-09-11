import sqlite3
import os

db_paths = [
    "/home/k1/ccia_workspace/art_62_probono.db",
    "/home/k1/ccia_workspace/swarm_memory/university.db"
]

print("=" * 80)
print("🛠️ PARCHEANDO ESQUEMA SQL Y LIMPIANDO SPAM EN BASES DE DATOS")
print("=" * 80)

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Asegurar tabla proposal_reviews con la columna timestamp
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proposal_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bounty_id TEXT,
        reviewer_id TEXT,
        score REAL,
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Verificar si falta la columna timestamp en caso de que la tabla existiera antes
    cursor.execute("PRAGMA table_info(proposal_reviews)")
    cols = [col[1] for col in cursor.fetchall()]
    if "timestamp" not in cols:
        try:
            cursor.execute("ALTER TABLE proposal_reviews ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
            print(f"  ✅ Columna 'timestamp' añadida a 'proposal_reviews' en {os.path.basename(db_path)}")
        except Exception as e:
            print(f"  ⚠️ No se pudo alterar tabla en {db_path}: {e}")

    # 2. Limpiar spam repetitivo de comment-auto-bot
    cursor.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%comment-auto-bot%' OR title LIKE '%comment-auto-bot%'")
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  🧹 Eliminados {deleted} registros de spam en {os.path.basename(db_path)}")

    conn.commit()
    conn.close()

print("=" * 80)
print("✅ LIMPIEZA Y REPARACIÓN DE TABLAS COMPLETADA")
print("=" * 80)
