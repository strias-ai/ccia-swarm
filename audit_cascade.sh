#!/usr/bin/env bash
echo "=========================================================================="
echo "🔍 1. REGISTROS DE STRIPE EN BASE DE DATOS (university.db)"
echo "=========================================================================="
sqlite3 /home/k1/ccia_workspace/university.db "SELECT 'Processed Events:', COUNT(*) FROM processed_stripe_events;"
sqlite3 /home/k1/ccia_workspace/university.db "SELECT * FROM processed_stripe_events ORDER BY id DESC LIMIT 5;"
sqlite3 /home/k1/ccia_workspace/university.db "SELECT 'Subscriptions:', COUNT(*) FROM user_subscriptions;"
sqlite3 /home/k1/ccia_workspace/university.db "SELECT * FROM user_subscriptions ORDER BY id DESC LIMIT 5;"

echo -e "\n=========================================================================="
echo "📜 2. LOGS DEL LISTENER DE STRIPE (ARTEFACTO #2)"
echo "=========================================================================="
if [ -f /home/k1/ccia_workspace/logs/stripe_webhooks.log ]; then
    tail -n 25 /home/k1/ccia_workspace/logs/stripe_webhooks.log
else
    echo "⚠️ Archivo /home/k1/ccia_workspace/logs/stripe_webhooks.log no encontrado."
fi

echo -e "\n=========================================================================="
echo "⚙️ 3. PROCESOS Y SERVICIOS ACTIVOS EN SEGUNDO PLANO"
echo "=========================================================================="
ps aux | grep -E "chronos|stripe|payout|settlement" | grep -v grep

echo -e "\n=========================================================================="
echo "📜 4. LOGS DEL PLANIFICADOR AUTÓNOMO (CHRONOS)"
echo "=========================================================================="
if [ -f /home/k1/ccia_workspace/logs/chronos_daemon.log ]; then
    tail -n 25 /home/k1/ccia_workspace/logs/chronos_daemon.log
else
    echo "⚠️ Archivo /home/k1/ccia_workspace/logs/chronos_daemon.log no encontrado."
fi

echo -e "\n=========================================================================="
echo "🛡️ 5. ESTADO DEL SERVICIO SYSTEMD (ccia-chronos)"
echo "=========================================================================="
sudo systemctl status ccia-chronos.service --no-pager
