import os
import sqlite3

WORKSPACE = "/home/k1/ccia_workspace"
PUB_PATH = os.path.join(WORKSPACE, "github_outbound_publisher.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("==================================================================")
print(" 📡 AUDITORÍA DE PUBLICACIÓN OUTBOUND (GITHUB <-> ISSUEHUNT)")
print("==================================================================")

if os.path.exists(PUB_PATH):
    with open(PUB_PATH, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()
    print("✅ Archivo 'github_outbound_publisher.py' localizado.")
    print(f"   Tamaño: {len(code.splitlines())} líneas.")
    
    # Verificar si soporta parseo de issue_url para extraer propietario/repo
    if "issue_url" in code or "repo" in code:
        print("  🟢 Mapeo de repositorio y URL de issue activo.")
    else:
        print("  ⚠️ El publicador requiere actualización de extracción de repo/issue.")
else:
    print("⚠️ 'github_outbound_publisher.py' no existe en la raíz de workspace.")

# Comprobar si hay bounties resueltos pendientes de publicación
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status IN ('RESOLVED', 'APPROVED')")
resolved_count = c.fetchone()[0]
conn.close()

print(f"📊 Bounties listos para envío inmediato: {resolved_count}")
print("==================================================================")
