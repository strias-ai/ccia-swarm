#!/bin/bash
set -euo pipefail

WORKSPACE_DIR="/home/k1/ccia_workspace"
LOG_FILE="$WORKSPACE_DIR/api_backend_jwt/logs/autonomous_loop.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CCIA-ORCHESTRATOR-V6.0] Iniciando ciclo..." | tee -a "$LOG_FILE"
python3 "$WORKSPACE_DIR/ccia_orchestrator.py" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CCIA-ORCHESTRATOR-V6.0] Ciclo finalizado." | tee -a "$LOG_FILE"
