import sqlite3

db_path = "/home/k1/ccia_workspace/university.db"

def fix_schema():
    print("🛠️ Verificando y adaptando esquema DB en university.db...")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Verificar columnas de bounty_opportunities
        cur.execute("PRAGMA table_info(bounty_opportunities);")
        cols = [c[1] for c in cur.fetchall()]
        
        if "state" not in cols and "status" not in cols:
            print("➕ Añadiendo columna 'state' a 'bounty_opportunities'...")
            cur.execute("ALTER TABLE bounty_opportunities ADD COLUMN state TEXT DEFAULT 'NEW';")
            conn.commit()
            print("✅ Columna 'state' añadida.")
        else:
            print(f"✅ Esquema verificado. Columnas existentes: {cols}")
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Error actualizando esquema: {e}")

fix_schema()
