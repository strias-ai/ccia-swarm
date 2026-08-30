import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Obtener los nombres de las columnas reales
cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
columns = [row[1] for row in cur.fetchall()]
print(f"📋 Columnas detectadas en ccia_artifact_manifests: {columns}")

manifest_25 = {
    "description": "Detección de anomalías cero-day por análisis de eventos únicos (frecuencia 1)",
    "table": "vant_agent_telemetry",
    "log": "/home/k1/ccia_workspace/cron_repos.log",
    "main_script": "/home/k1/ccia_workspace/modules/hapax_log_sentinel.py",
    "script": "/home/k1/ccia_workspace/modules/hapax_log_sentinel.py"
}

manifest_26 = {
    "description": "API Metered Billing para congelar e hidratar estado conversacional/vectorial de agentes de IA",
    "table": "anhydro_vault",
    "log": "/home/k1/ccia_workspace/cron_repos.log",
    "main_script": "/home/k1/ccia_workspace/modules/anhydro_vault_api.py",
    "script": "/home/k1/ccia_workspace/modules/anhydro_vault_api.py"
}

# Map de valores según esquema flexible
def build_insert_dict(art_id, name, ver, cat, script, log_f, manifest_dict):
    data = {}
    for col in columns:
        col_lower = col.lower()
        if col_lower == 'artifact_id':
            data[col] = art_id
        elif col_lower == 'name':
            data[col] = name
        elif col_lower == 'version':
            data[col] = ver
        elif col_lower == 'category':
            data[col] = cat
        elif col_lower in ('main_script', 'script', 'target'):
            data[col] = script
        elif 'log' in col_lower:
            data[col] = log_f
        elif col_lower in ('certification_status', 'status'):
            data[col] = 'CERTIFIED'
        elif col_lower in ('manifest_json', 'manifest'):
            data[col] = json.dumps(manifest_dict)
        elif col_lower in ('created_at', 'updated_at'):
            continue  # Dejar a SQLite el default TIMESTAMP
        else:
            data[col] = None
    return data

art25_data = build_insert_dict('25', 'Hapax Log Sentinel (Detección Anomalías Zero-Day)', 'v1.0.0', 'Auditoría & Calidad', '/home/k1/ccia_workspace/modules/hapax_log_sentinel.py', '/home/k1/ccia_workspace/cron_repos.log', manifest_25)
art26_data = build_insert_dict('26', 'Anhydro-Vault API (Vector 4: Cold-State AI Agents)', 'v1.0.0', 'Core API & Auth', '/home/k1/ccia_workspace/modules/anhydro_vault_api.py', '/home/k1/ccia_workspace/cron_repos.log', manifest_26)

for art in [art25_data, art26_data]:
    cols = [k for k in art.keys() if art[k] is not None]
    vals = [art[k] for k in cols]
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({', '.join(cols)}) VALUES ({placeholders})"
    cur.execute(sql, vals)

conn.commit()
conn.close()

print("🟢 Artefactos 25 y 26 registrados con éxito en university.db.")
