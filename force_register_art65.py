import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Leer estructura real de columnas
cursor.execute("PRAGMA table_info(ccia_artifact_manifests);")
cols_info = cursor.fetchall()
col_names = [c[1] for c in cols_info]

print("=" * 80)
print(f"📊 Columnas reales de 'ccia_artifact_manifests': {col_names}")

# 2. Mapear datos según las columnas reales existentes
row_data = {}
for col in col_names:
    cl = col.lower()
    if any(k in cl for k in ['id', 'num', 'option']):
        row_data[col] = 65
    elif any(k in cl for k in ['name', 'title', 'artifact']):
        row_data[col] = 'CCiA Swarm API Gateway & Inter-Agent Tool Bus'
    elif 'version' in cl:
        row_data[col] = 'v1.0.0'
    elif 'cat' in cl:
        row_data[col] = 'SWARM_API_GATEWAY'
    elif 'status' in cl:
        row_data[col] = 'CERTIFIED'
    elif any(k in cl for k in ['path', 'file', 'script']):
        row_data[col] = '/home/k1/ccia_workspace/modules/art_65.py'
    else:
        row_data[col] = 'N/A'

fields = ", ".join(row_data.keys())
placeholders = ", ".join(["?"] * len(row_data))
query = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({fields}) VALUES ({placeholders})"

cursor.execute(query, list(row_data.values()))
conn.commit()
conn.close()

print("✅ Artefacto 65 insertado correctamente en university.db.")
print("=" * 80)
