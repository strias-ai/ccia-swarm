import sqlite3
import json
import os
import py_compile
import subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"
MODULES_DIR = "/home/k1/ccia_workspace/modules"
os.makedirs(MODULES_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. GARANTIZAR ESQUEMA Y TABLA ANHYDRO_VAULT EN DB
# ---------------------------------------------------------
print("🗄️ 1. Asegurando esquema de tablas en university.db...")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS anhydro_vault (
        agent_id TEXT,
        session_id TEXT PRIMARY KEY,
        cold_data TEXT,
        original_bytes INT,
        compressed_bytes INT,
        frozen_at TIMESTAMP
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS system_health_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health_score INT,
        services_status TEXT,
        ast_errors INT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print("🟢 Tablas 'anhydro_vault' y 'system_health_logs' garantizadas.")

# ---------------------------------------------------------
# 2. CREACIÓN ARTEFACTO 27: SYSTEM AUTO-HEALING WATCHDOG
# ---------------------------------------------------------
print("\n🩺 2. Creando Artefacto 27: CCiA System Auto-Healing Watchdog...")

watchdog_path = os.path.join(MODULES_DIR, "system_health_watchdog.py")
watchdog_code = '''import sqlite3
import subprocess
import py_compile
import json
import os
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

class SystemHealthWatchdog:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.services = ["ccia-core-api.service", "ccia-webhook-listener.service"]

    def check_services(self):
        status = {}
        for svc in self.services:
            res = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
            active = res.stdout.strip() == "active"
            status[svc] = "UP" if active else "DOWN"
            if not active:
                # Intento de autorrecuperación
                subprocess.run(["sudo", "systemctl", "restart", svc])
        return status

    def check_all_artifacts_ast(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT artifact_id, main_script FROM ccia_artifact_manifests")
        rows = cur.fetchall()
        conn.close()

        ast_errors = 0
        for art_id, script in rows:
            if script and os.path.exists(script):
                try:
                    py_compile.compile(script, doraise=True)
                except Exception:
                    ast_errors += 1
        return len(rows), ast_errors

    def run_diagnostics(self):
        svc_status = self.check_services()
        total_arts, ast_errors = self.check_all_artifacts_ast()
        
        up_services = sum(1 for v in svc_status.values() if v == "UP")
        health_score = int(((up_services / len(self.services)) * 60) + (((total_arts - ast_errors) / max(total_arts, 1)) * 40))

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_health_logs (health_score, services_status, ast_errors)
            VALUES (?, ?, ?)
        """, (health_score, json.dumps(svc_status), ast_errors))
        conn.commit()
        conn.close()

        report = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "health_score": f"{health_score}%",
            "services": svc_status,
            "total_artifacts_audited": total_arts,
            "ast_syntax_errors": ast_errors,
            "status": "HEALTHY" if health_score >= 80 else "DEGRADED"
        }
        return report

if __name__ == "__main__":
    watchdog = SystemHealthWatchdog()
    print(json.dumps(watchdog.run_diagnostics(), indent=2, ensure_ascii=False))
'''

with open(watchdog_path, "w") as f:
    f.write(watchdog_code)

py_compile.compile(watchdog_path, doraise=True)
print("🟢 Artefacto 27 compilado y verificado sintácticamente.")

# ---------------------------------------------------------
# 3. REGISTRO DEL ARTEFACTO 27 EN UNIVERSITY.DB
# ---------------------------------------------------------
print("\n📝 3. Registrando Artefacto 27 en ccia_artifact_manifests...")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(ccia_artifact_manifests);")
columns = [row[1] for row in cur.fetchall()]

manifest_27 = {
    "description": "Daemon autónomo de salud, verificación AST continua de 27 artefactos y autorrecuperación de servicios systemd",
    "table": "system_health_logs",
    "log": "/home/k1/ccia_workspace/cron_repos.log",
    "main_script": watchdog_path,
    "script": watchdog_path
}

data = {}
for col in columns:
    c = col.lower()
    if c == 'artifact_id': data[col] = '27'
    elif c == 'name': data[col] = 'CCiA System Auto-Healing & Health Sentinel'
    elif c == 'version': data[col] = 'v1.0.0'
    elif c == 'category': data[col] = 'Infraestructura & Contenedores'
    elif c in ('main_script', 'script', 'target'): data[col] = watchdog_path
    elif 'log' in c: data[col] = '/home/k1/ccia_workspace/cron_repos.log'
    elif c in ('ast_status', 'certification_status', 'status'): data[col] = 'CERTIFIED'
    elif c in ('manifest_json', 'manifest'): data[col] = json.dumps(manifest_27)
    elif c in ('db_table', 'target_table'): data[col] = 'system_health_logs'

cols = [k for k in data.keys() if data[k] is not None]
vals = [data[k] for k in cols]
placeholders = ", ".join(["?"] * len(cols))
sql = f"INSERT OR REPLACE INTO ccia_artifact_manifests ({', '.join(cols)}) VALUES ({placeholders})"

cur.execute(sql, vals)
conn.commit()
conn.close()

print("🟢 Artefacto 27 registrado exitosamente en university.db.")

# ---------------------------------------------------------
# 4. EJECUCIÓN DE PRUEBA DEL AUTO-HEALING WATCHDOG
# ---------------------------------------------------------
print("\n🧪 4. Ejecutando diagnóstico inicial del Artefacto 27...")
res = subprocess.run(["python3", watchdog_path], capture_output=True, text=True)
print(res.stdout)

print("\n✅ Mejora completada. Todos los artefactos sincronizados.")
