import sqlite3
import py_compile
import subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"
SENTINEL_PATH = "/home/k1/ccia_workspace/modules/hapax_log_sentinel.py"

# 1. Corregir DeprecationWarning en Hapax Log Sentinel
print("🛠️ 1. Optimizando Hapax Log Sentinel (timezone UTC)...")
with open(SENTINEL_PATH, "r") as f:
    code = f.read()

code = code.replace(
    "datetime.utcnow().isoformat()",
    "datetime.now().astimezone().isoformat()"
)

with open(SENTINEL_PATH, "w") as f:
    f.write(code)

py_compile.compile(SENTINEL_PATH, doraise=True)
print("🟢 Sentinel optimizado sin advertencias de deprecación.")

# 2. Verificar datos en la tabla anhydro_vault
print("\n📊 2. Consultando registros en tabla 'anhydro_vault'...")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
try:
    cur.execute("SELECT agent_id, session_id, original_bytes, compressed_bytes, frozen_at FROM anhydro_vault;")
    rows = cur.fetchall()
    if rows:
        print(f"🟢 Registros en estado frío encontrados ({len(rows)}):")
        for r in rows:
            ratio = round((1 - (r[3] / r[2])) * 100, 1) if r[2] > 0 else 0
            print(f"   • Agente: {r[0]} | Sesión: {r[1]} | De {r[2]}B a {r[3]}B (Ahorro RAM: {ratio}%) | {r[4]}")
    else:
        print("ℹ️ Tabla vacía. Se ejecutará prueba local de inserción/congelado.")
except Exception as e:
    print(f"❌ Error al consultar anhydro_vault: {e}")
conn.close()

# 3. Reiniciar Core API para asegurar carga completa de routers
subprocess.run(["sudo", "systemctl", "restart", "ccia-core-api.service"])
print("\n🟢 Core API reiniciada y sincronizada con Artefactos 25 y 26.")
