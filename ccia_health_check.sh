#!/usr/bin/env bash

# ==============================================================================
# CCIA SYSTEM HEALTH & HARDWARE/SOFTWARE DIAGNOSTIC AUDIT
# ==============================================================================

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}"
echo "================================================================================"
echo "      🛸 CCIA SYSTEM HEALTH AUDIT & DIAGNOSTIC INSPECTOR (READ-ONLY)"
echo "================================================================================"
echo -e "${RESET}"

# 1. INFORMACIÓN DEL SISTEMA Y CPU
echo -e "${BOLD}[1/10] 💻 Carga de Procesador y Kernel${RESET}"
echo "--------------------------------------------------------------------------------"
echo "OS / Kernel:   $(uname -sr) ($(uname -m))"
echo "Uptime / Carga: $(uptime)"
echo "Modelo CPU:    $(lscpu | grep "Model name" | sed 's/Model name:\s*//')"
echo "Núcleos CPU:   $(nproc) hilos disponibles"
echo ""

# 2. MEMORIA RAM Y SWAP
echo -e "${BOLD}[2/10] 🧠 Estado de Memoria RAM y SWAP${RESET}"
echo "--------------------------------------------------------------------------------"
free -h
echo ""

# 3. TOP 20 PROCESOS POR CONSUMO DE RAM
echo -e "${BOLD}[3/10] 📊 Top 20 Procesos por Consumo de Memoria RAM${RESET}"
echo "--------------------------------------------------------------------------------"
ps aux --sort=-%mem | awk 'NR==1{print $0} NR>1{print $0}' | head -n 21
echo ""

# 4. ESPACIO EN DISCO E INODOS
echo -e "${BOLD}[4/10] 💾 Almacenamiento en Disco e Inodos${RESET}"
echo "--------------------------------------------------------------------------------"
df -h -x tmpfs -x devtmpfs -x overlay
echo ""
echo "Estado de Inodos:"
df -i -x tmpfs -x devtmpfs -x overlay
echo ""

# 5. ESTADO DE GPU (NVIDIA / AMD)
echo -e "${BOLD}[5/10] 🎮 VRAM y Procesadores Gráficos (GPU)${RESET}"
echo "--------------------------------------------------------------------------------"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
elif command -v rocm-smi &> /dev/null; then
    rocm-smi
else
    echo "ℹ️ No se detectó utilidades de GPU dedicada (nvidia-smi / rocm-smi) o no hay controlador instalado."
fi
echo ""

# 6. DOCKER Y CONTENEDORES ACTIVOS
echo -e "${BOLD}[6/10] 🐳 Contenedores Docker Activos${RESET}"
echo "--------------------------------------------------------------------------------"
if command -v docker &> /dev/null; then
    docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "⚠️ No se pudo acceder al socket de Docker (permisos requeridos)."
else
    echo "ℹ️ Docker no está instalado en el sistema."
fi
echo ""

# 7. PUERTOS Y SERVIDORES ACTIVOS
echo -e "${BOLD}[7/10] 🌐 Puertos Abiertos y Escuchando (TCP/UDP)${RESET}"
echo "--------------------------------------------------------------------------------"
if command -v ss &> /dev/null; then
    ss -tulpn | grep LISTEN
else
    netstat -tulpn | grep LISTEN
fi
echo ""

# 8. SERVICIOS SYSTEMD Y DEMONIOS EN EJECUCIÓN
echo -e "${BOLD}[8/10] ⚙️ Demonios y Servicios Activos (Systemd)${RESET}"
echo "--------------------------------------------------------------------------------"
systemctl list-units --type=service --state=running --no-pager | head -n 25
echo ""

# 9. COMPONENTES CCIA & SERVICIOS CLAVE (Ollama, Tailscale, SQLite)
echo -e "${BOLD}[9/10] 🧩 Entorno Específico CCIA, Ollama y Tailscale${RESET}"
echo "--------------------------------------------------------------------------------"
echo -n "Ollama Engine (11434): "
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${GREEN}ONLINE${RESET}"
else
    echo -e "${RED}OFFLINE / No responde${RESET}"
fi

echo -n "Gateway A2A CCiA (8089): "
if ss -tulpn 2>/dev/null | grep -q ":8089"; then
    echo -e "${GREEN}ONLINE (Puerto 8089 activo)${RESET}"
else
    echo -e "${YELLOW}OFFLINE (Servidor A2A no levantado)${RESET}"
fi

echo -n "Tailscale Mesh: "
if command -v tailscale &> /dev/null; then
    tailscale status 2>/dev/null | head -n 3 || echo -e "${YELLOW}Inactivo o requiriendo login${RESET}"
else
    echo "No instalado."
fi

if [ -f "/home/k1/ccia_workspace/university.db" ]; then
    DB_SIZE=$(du -sh /home/k1/ccia_workspace/university.db | cut -f1)
    echo "Base de Datos CCiA (university.db): $DB_SIZE"
else
    echo "Base de Datos CCiA (university.db): No localizada en la ruta por defecto."
fi
echo ""

# 10. REVISIÓN EXTRA: ERRORES DE SISTEMA Y OOM KILLER
echo -e "${BOLD}[10/10] ⚠️ Logs Críticos Recientes (OOM Killer / Kernel Errors)${RESET}"
echo "--------------------------------------------------------------------------------"
echo "OOM (Out of Memory) Events:"
dmesg -T 2>/dev/null | grep -i "out of memory" | tail -n 5 || echo "Sin eventos de falta de memoria (OOM) en kernel."
echo ""
echo "Errores Systemd (Journalctl - Prioridad 3):"
journalctl -p 3 -xb --no-pager -n 5 2>/dev/null || echo "Sin registros recientes de error crítico en el diario de sistema."
echo ""

# ==============================================================================
# RESUMEN EXECUTIVO PARA COPIAR AL CHAT
# ==============================================================================

# Métricas rápidas para el cuadro
RAM_TOTAL=$(free -h | awk '/Mem:/ {print $2}')
RAM_USED=$(free -h | awk '/Mem:/ {print $3}')
RAM_FREE=$(free -h | awk '/Mem:/ {print $4}')
SWAP_USED=$(free -h | awk '/Swap:/ {print $3}')
DISK_ROOT_PCT=$(df -h / | awk 'NR==2 {print $5}')
DISK_ROOT_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }' | sed 's/^[ \t]*//')
DOCKER_COUNT=$(docker ps -q 2>/dev/null | wc -l)
OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags &> /dev/null && echo "ONLINE" || echo "OFFLINE")
A2A_STATUS=$(ss -tulpn 2>/dev/null | grep -q ":8089" && echo "ONLINE" || echo "OFFLINE")

echo -e "${GREEN}${BOLD}"
echo "╭──────────────────────────────────────────────────────────────────────────────╮"
echo "│                 📋 RESUMEN DE SALUD CCIA PARA REVISIÓN                      │"
echo "├──────────────────────────────────────────────────────────────────────────────┤"
printf "│ %-30s : %-43s │\n" "Fecha Audit" "$(date '+%Y-%m-%d %H:%M:%S')"
printf "│ %-30s : %-43s │\n" "Carga CPU (1, 5, 15 min)" "$LOAD_AVG"
printf "│ %-30s : %-43s │\n" "Memoria RAM (Usada/Total)" "$RAM_USED / $RAM_TOTAL (Libre: $RAM_FREE)"
printf "│ %-30s : %-43s │\n" "Memoria SWAP Usada" "$SWAP_USED"
printf "│ %-30s : %-43s │\n" "Espacio Disco / (Libre / %)" "$DISK_ROOT_AVAIL ($DISK_ROOT_PCT ocupado)"
printf "│ %-30s : %-43s │\n" "Contenedores Docker Activos" "$DOCKER_COUNT contenedores"
printf "│ %-30s : %-43s │\n" "Servidor Ollama (11434)" "$OLLAMA_STATUS"
printf "│ %-30s : %-43s │\n" "Gateway A2A CCiA (8089)" "$A2A_STATUS"
if command -v nvidia-smi &> /dev/null; then
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | awk -F', ' '{print $1"MB / "$2"MB"}')
    printf "│ %-30s : %-43s │\n" "VRAM GPU Usada" "$GPU_MEM"
fi
echo "╰──────────────────────────────────────────────────────────────────────────────╯"
echo -e "${RESET}"
echo "👉 Copia el bloque delimitado por 'RESUMEN DE SALUD CCIA' y pégalo aquí para analizarlo."

