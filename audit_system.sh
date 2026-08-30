#!/bin/bash
echo "================================================================="
echo "📊 AUDITORÍA DEL SISTEMA CCIA MONETIZACIÓN & BOUNTIES"
echo "================================================================="

echo "1. Estado de los Servicios Systemd:"
systemctl is-active --quiet ccia-webhook-listener && echo "  - Webhook Listener (8080): 🟢 RUNNING" || echo "  - Webhook Listener (8080): 🔴 STOPPED"
systemctl is-active --quiet ccia-core-api && echo "  - Core API FastAPI (8000): 🟢 RUNNING" || echo "  - Core API FastAPI (8000): 🔴 STOPPED"
systemctl is-active --quiet ccia-ngrok && echo "  - Ngrok Tunnel Service: 🟢 RUNNING" || echo "  - Ngrok Tunnel Service: 🔴 STOPPED"

echo ""
echo "2. Estado Actual de Suscripciones (university.db):"
sqlite3 -header -column /home/k1/ccia_workspace/university.db "SELECT user_email, stripe_customer_id, status, updated_at FROM subscriptions LIMIT 5;"

echo ""
echo "3. Bounties Autónomos Capturados (Vector 1):"
sqlite3 -header -column /home/k1/ccia_workspace/university.db "SELECT repo_name, bounty_amount, status, created_at FROM bounties_captured;" 2>/dev/null || echo "No hay registros de bounties aún."

echo ""
echo "4. Últimos Eventos Stripe Procesados:"
sqlite3 -header -column /home/k1/ccia_workspace/university.db "SELECT event_id, event_type, amount, processed_at FROM processed_events ORDER BY processed_at DESC LIMIT 3;"
echo "================================================================="
