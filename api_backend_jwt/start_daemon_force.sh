#!/bin/bash
export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1

TARGET_DIR="/home/k1/ccia_workspace/api_backend_jwt"
cd "$TARGET_DIR" || exit 1

echo "=== 1. Deteniendo instancias previas y limpiando PID ==="
python3 "$TARGET_DIR/university_scheduler.py" --stop >/dev/null 2>&1
rm -f "$TARGET_DIR/scheduler.pid"

echo "=== 2. Lanzando Demonio Universitario (Modo Unbuffered) ==="
nohup python3 -u "$TARGET_DIR/university_scheduler.py" --start > "$TARGET_DIR/university_scheduler.log" 2>&1 &
DAEMON_PID=$!

sleep 3

echo "=== 3. Estado del Demonio ==="
python3 "$TARGET_DIR/university_scheduler.py" --status

echo ""
echo "=== 4. Primeras líneas registradas en university_scheduler.log ==="
cat "$TARGET_DIR/university_scheduler.log"
