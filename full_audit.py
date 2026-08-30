import os
import sqlite3
import subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"

print("=================================================================")
print("🔍 AUDITORÍA DE SALUD Y DEUDA TÉCNICA CCIA (23 ARTEFACTOS)")
print("=================================================================\n")

# 1. Integridad de los 23 Artefactos en Disco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT artifact_id, name, main_script FROM ccia_artifact_manifests ORDER BY CAST(artifact_id AS INTEGER)")
artifacts = cursor.fetchall()

missing_files = 0
print("1. Verificación de Artefactos Registrados vs Archivos Reales:")
for art_id, name, script_path in artifacts:
    exists = os.path.exists(script_path) if script_path else False
    status = "🟢 DISPONIBLE" if exists else "🔴 FALTA EN DISCO"
    if not exists:
        missing_files += 1
    print(f"  [{art_id:>2}] {name[:48]:<48} -> {status}")

print(f"\n Total Artefactos: {len(artifacts)} | Deuda Técnica (Faltantes): {missing_files}\n")

# 2. Métricas y Registros de la Base de Datos
cursor.execute("SELECT count(*) FROM bounties")
bounties_count = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM ccia_artifact_manifests")
manifests_count = cursor.fetchone()[0]

print("2. Métricas Internas (university.db):")
print(f"  - Registro de Bounties / Oportunidades: {bounties_count}")
print(f"  - Manifiestos Certificados:             {manifests_count}\n")
conn.close()

# 3. Estado de Servicios Clave
print("3. Estado de Servicios Systemd en Ejecución:")
services = ["ccia-webhook-listener.service", "ccia-core-api.service"]
for svc in services:
    res = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True).stdout.strip()
    icon = "🟢 RUNNING" if res == "active" else "🔴 STOPPED"
    print(f"  - {svc}: {icon}")

