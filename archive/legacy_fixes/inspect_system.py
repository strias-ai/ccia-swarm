import sqlite3
import shutil

DB_PATH = "/home/k1/ccia_workspace/university.db"

print("=================================================================")
print("🧠 INSPECCIÓN DE AGENTES, BIBLIOTECA & SALUD MONETIZADORA CCIA")
print("=================================================================\n")

# 1. Verificación de Espacio en Disco en NucBox
total, used, free = shutil.disk_usage("/")
print(f"💾 ESTADO DEL DISCO DUDO (NVMe NucBox):")
print(f"  - Espacio Libre: {free // (2**30)} GB")
print(f"  - Espacio Usado: {used // (2**30)} GB")
print(f"  - Espacio Total: {total // (2**30)} GB\n")

# 2. Inspección de Estructuras y Tablas en university.db
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

print("📚 ESTRUCTURA DE LA UNIVERSIDAD & BIBLIOTECA (university.db):")
for t in tables:
    cursor.execute(f"SELECT count(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"  - Tabla [{t:<32}]: {count} registros")

print("\n📈 EVOLUCIÓN DE DEMANDA Y MONETIZACIÓN DE PROYECTOS:")
if "bounties" in tables:
    cursor.execute("SELECT status, count(*), COALESCE(SUM(bounty_amount), 0.0) FROM bounties GROUP BY status")
    stats = cursor.fetchall()
    if stats:
        for status, count, total_usd in stats:
            print(f"  - Estado: {status:<16} | Cantidad: {count:<3} | Proyección USD: ${total_usd:.2f}")
    else:
        print("  - Sin transacciones registradas en bounties.")

conn.close()
