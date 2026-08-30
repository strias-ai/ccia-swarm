#!/bin/bash
echo "🚀 [DAEMON CCIA] Iniciando servicio en segundo plano..."
while true; do
    python3 /home/k1/ccia_workspace/ccia_orchestrator.py >> /home/k1/ccia_workspace/api_backend_jwt/logs/autonomous_loop.log 2>&1
    sleep 60
done
