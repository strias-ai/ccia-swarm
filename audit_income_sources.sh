#!/usr/bin/env bash
DB="/home/k1/ccia_workspace/university.db"

echo "=========================================================================="
echo "🔎 1. REGISTROS EN REVENUE_SETTLEMENTS (Detalle Completo)"
echo "=========================================================================="
sqlite3 -header -column $DB "SELECT * FROM revenue_settlements;"

echo -e "\n=========================================================================="
echo "🔎 2. OTRAS TABLAS DE MONETIZACIÓN Y TRANSACCIONES"
echo "=========================================================================="
tables=$(sqlite3 $DB "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%bounty%' OR name LIKE '%escrow%' OR name LIKE '%transaction%' OR name LIKE '%settle%' OR name LIKE '%payout%' OR name LIKE '%revenue%');")

for tbl in $tables; do
    echo "--- Tabla: $tbl ---"
    sqlite3 -header -column $DB "SELECT * FROM $tbl LIMIT 10;"
    echo ""
done

echo "=========================================================================="
echo "🔎 3. REGISTROS DE EVENTOS O WEBHOOKS RECIBIDOS"
echo "=========================================================================="
sqlite3 -header -column $DB "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%event%';"
