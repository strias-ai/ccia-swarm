#!/bin/bash
# 🛸 CCIA PERSISTENT TUNNEL DAEMON
LOG_FILE="/home/k1/ccia_workspace/api_backend_jwt/logs/tunnel.log"

echo "🚀 Iniciando Túnel Público HTTPS en segundo plano..."
pkill -f "nokey@localhost.run" || true

nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 nokey@localhost.run > "$LOG_FILE" 2>&1 &

sleep 3
echo "✅ Túnel activo en segundo plano. URL asignada:"
grep -o "https://[a-zA-Z0-9]*\.lhr\.life" "$LOG_FILE" | tail -n 1
