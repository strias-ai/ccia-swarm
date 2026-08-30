#!/bin/bash
LOG_FILE="/home/k1/ccia_workspace/api_backend_jwt/logs/cf_tunnel.log"

echo "🚀 Iniciando Túnel Cloudflare Quick en segundo plano..."
pkill -f "cloudflared tunnel" || true

nohup cloudflared tunnel --url http://localhost:8000 > "$LOG_FILE" 2>&1 &

sleep 4
echo "✅ Túnel Cloudflare asignado:"
grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" "$LOG_FILE" | tail -n 1
