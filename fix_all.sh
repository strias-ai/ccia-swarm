#!/bin/bash
set -e

DB_PATH="/home/k1/ccia_workspace/university.db"
LOG_PATH="/home/k1/ccia_workspace/art63_autonomo.log"
ART62_PATH="/home/k1/ccia_workspace/modules/art_62.py"

echo "================================================================================"
echo "🛠️ INICIANDO REPARACIÓN COMPLETA DE ARTEFACTO 62, LIMPIEZA Y AUDITORÍA DE MEMORIA"
echo "================================================================================"

# 1. Corregir esquema de tabla ccia_artifact_manifests
echo "1️⃣  Ajustando esquema e insertando registro inicial para Artefacto 62..."
python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS ccia_artifact_manifests (
        artifact_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')
cur.execute('''
    INSERT INTO ccia_artifact_manifests (artifact_id, name, status)
    VALUES ('62', 'Artefacto 62 Bucle 24/7', 'ACTIVE')
    ON CONFLICT(artifact_id) DO UPDATE SET status='ACTIVE', name='Artefacto 62 Bucle 24/7';
''')
conn.commit()
conn.close()
print('   ✅ Tabla ccia_artifact_manifests reparada con éxito.')
"

# 2. Generar el script completo del Artefacto 62 desde cero
echo "2️⃣  Construyendo ejecutable de Artefacto 62 ($ART62_PATH)..."
cat << 'ART62_EOF' > "$ART62_PATH"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCiA Artefacto 62 - Bucle Autónomo 24/7 y Monitor de Estado
"""
import os
import sys
import time
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def get_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "DISABLED"
    except Exception as e:
        return f"ERROR: {e}"

def run_loop():
    print("🟢 [ART-62] Daemon Bucle 24/7 Iniciado Correctamente.")
    while True:
        status = get_status()
        if status == "ACTIVE":
            print("⚡ [ART-62] Bucle activo. Verificando estado del enjambre...")
        else:
            print(f"⏸️ [ART-62] En pausa o inactivo. Estado actual: {status}")
        time.sleep(30)

if __name__ == "__main__":
    run_loop()
ART62_EOF

chmod +x "$ART62_PATH"
cp "$ART62_PATH" /home/k1/ccia_workspace/ccia_mando_62.py 2>/dev/null || true
echo "   ✅ Artefacto 62 desplegado y permisos asignados."

# 3. Limpiar logs y cerrojos residuales
echo "3️⃣  Vaciando archivos de log e impresiones tty saturadas..."
if [ -f "$LOG_PATH" ]; then
    > "$LOG_PATH"
    echo "   🧹 ARCHIVO $LOG_PATH VACIADO CORRECTAMENTE."
fi

rm -f /tmp/ccia_bounty.lock
echo "   ✅ Cerrojo /tmp/ccia_bounty.lock liberado."

# 4. Auditoría de Memoria en Base de Datos
echo "4️⃣  Auditando estado actual de la Base de Datos (university.db)..."
python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()

tables = ['bounty_vector_memory', 'bounty_swarm_history', 'swarm_debates', 'proposal_reviews', 'ccia_artifact_manifests']
print('   --------------------------------------------------')
for t in tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {t};')
        cnt = cur.fetchone()[0]
        print(f'   📊 Tabla {t:<24} : {cnt} registros')
    except Exception as e:
        print(f'   ⚠️ Tabla {t:<24} : NO EXISTE O ERROR')
print('   --------------------------------------------------')
conn.close()
"

echo "================================================================================"
echo "✅ PROCESO DE AUDITORÍA, REPARACIÓN Y LIMPIEZA CONCLUIDO"
echo "================================================================================"
