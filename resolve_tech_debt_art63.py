import sqlite3
import subprocess
import json
import os
import time

print("================================================================================")
print("🛠️ RESOLVIENDO DEUDA TÉCNICA DEL ARTEFACTO 63 (ESQUEMA + DAEMON + VECTOR MEMORY)")
print("================================================================================")

DB_PATH = "/home/k1/ccia_workspace/university.db"

# 1. Reconstruir esquema de bounty_vector_memory de forma limpia
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS bounty_vector_memory")
cursor.execute("""
    CREATE TABLE bounty_vector_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artifact_id TEXT UNIQUE,
        text_content TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()

# 2. Cargar las 63 filas de ccia_artifact_manifests a bounty_vector_memory
cursor.execute("PRAGMA table_info(ccia_artifact_manifests)")
cols = [row[1] for row in cursor.fetchall()]

cursor.execute("SELECT * FROM ccia_artifact_manifests")
rows = cursor.fetchall()

inserted = 0
for row in rows:
    row_dict = {cols[i]: str(row[i]) for i in range(len(cols))}
    art_id = row_dict.get("artifact_id") or row_dict.get("id") or str(inserted + 1)
    content = " | ".join([f"{k}: {v}" for k, v in row_dict.items() if v and v != "None"])
    
    cursor.execute(
        "INSERT OR REPLACE INTO bounty_vector_memory (artifact_id, text_content, metadata) VALUES (?, ?, ?)",
        (f"artifact_{art_id}", content, json.dumps(row_dict))
    )
    inserted += 1

conn.commit()
conn.close()
print(f"✅ 1. Memoria vectorial reconstruida: {inserted} manifiestos registrados en 'bounty_vector_memory'.")

# 3. Iniciar el Daemon en segundo plano
daemon_script = "/home/k1/ccia_workspace/ccia_mando_63.py"
log_file = "/home/k1/ccia_workspace/daemon_63.log"

if os.path.exists(daemon_script):
    cmd = f"nohup python3 {daemon_script} --daemon > {log_file} 2>&1 &"
    os.system(cmd)
    time.sleep(1)
    print("✅ 2. Daemon de control 24/7 lanzado en segundo plano.")

print("================================================================================")
print("✨ CORRECCIÓN COMPLETADA")
print("================================================================================")
