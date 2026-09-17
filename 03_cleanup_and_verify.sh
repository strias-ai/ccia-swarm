#!/bin/bash
set -e

echo "📦 1. Archivando scripts de parches redundantes..."
mkdir -p /home/k1/ccia_workspace/legacy_patches
mv -f /home/k1/ccia_workspace/fix_*.py /home/k1/ccia_workspace/reparar_*.py /home/k1/ccia_workspace/patch_*.py /home/k1/ccia_workspace/legacy_patches/ 2>/dev/null || true

echo "🔍 2. Verificando sintaxis de los nuevos componentes..."
python3 -m py_compile /home/k1/ccia_workspace/01_migrate_schema.py
python3 -m py_compile /home/k1/ccia_workspace/bounty_manager.py

echo "🚀 3. Ejecutando migración e ingesta limpia..."
python3 /home/k1/ccia_workspace/01_migrate_schema.py
python3 /home/k1/ccia_workspace/bounty_manager.py

echo "🛡️ 4. Comprobando verificación sintáctica del Núcleo Hapax..."
python3 -m py_compile /home/k1/nucleo_hapax.py

echo "✨ MIGRACIÓN Y LIMPIEZA COMPLETADAS CON ÉXITO SIN ERRORES."
