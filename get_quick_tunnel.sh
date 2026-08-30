#!/bin/bash
pkill -f "cloudflared tunnel" || true
sleep 1

echo "⏳ Generando túnel de Cloudflare..."
cloudflared tunnel --url http://localhost:8000 > /tmp/cf_tunnel.log 2>&1 &

# Esperar a que cloudflared obtenga la URL
for i in {1..10}; do
    URL=$(grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" /tmp/cf_tunnel.log | tail -n 1)
    if [ -n "$URL" ]; then
        echo -e "\n=================================================="
        echo "✅ TU URL PÚBLICA PARA STRIPE WEBHOOK ES:"
        echo "$URL/webhook/stripe"
        echo "=================================================="
        exit 0
    fi
    sleep 1
done

echo "⚠️ No se pudo obtener la URL de Cloudflare. Revisa /tmp/cf_tunnel.log"
