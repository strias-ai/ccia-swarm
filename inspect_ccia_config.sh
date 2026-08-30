#!/usr/bin/env bash
DB="/home/k1/ccia_workspace/university.db"

echo "=========================================================================="
echo "🔎 1. TABLAS EXISTENTES EN LA BASE DE DATOS LOCAL (university.db)"
echo "=========================================================================="
sqlite3 $DB "SELECT name FROM sqlite_master WHERE type='table';"

echo -e "\n=========================================================================="
echo "🔎 2. ESQUEMA DE TABLAS RELACIONADAS CON CONFIGURACIÓN O CLAVES"
echo "=========================================================================="
sqlite3 -header -column $DB "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%stripe%' OR name LIKE '%config%' OR name LIKE '%key%' OR name LIKE '%agent%' OR name LIKE '%service%' OR name LIKE '%product%');"

echo -e "\n=========================================================================="
echo "🔎 3. BÚSQUEDA DE CLAVES STRIPE EN CÓDIGO Y ARCHIVOS .ENV"
echo "=========================================================================="
grep -rnw '/home/k1/ccia_workspace/' -e 'sk_live_' -e 'sk_test_' --exclude-dir={.git,__pycache__,node_modules} 2>/dev/null | head -n 10

echo -e "\n=========================================================================="
echo "🔎 4. ANÁLISIS DE AGENTES Y SUS MÓDULOS DE PROSPECCIÓN / OUTBOUND"
echo "=========================================================================="
echo "--- Archivos principales de agentes identificados ---"
ls -la /home/k1/ccia_workspace/api_backend_jwt/*.py 2>/dev/null
ls -la /home/k1/ccia_workspace/modules/*.py 2>/dev/null

echo -e "\n--- Búsqueda de capacidades HTTP Outbound (requests/httpx/aiohttp/scrapers) ---"
grep -rnE "(requests\.|httpx\.|aiohttp\.|fetch|stripe\.)" /home/k1/ccia_workspace/ --exclude-dir={.git,__pycache__,node_modules} | head -n 15

