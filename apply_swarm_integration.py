#!/usr/bin/env python3
import re
from pathlib import Path

bridge_path = Path("/home/k1/ccia_workspace/modules/art_65_bridge.py")

if bridge_path.exists():
    content = bridge_path.read_text(encoding="utf-8")
    
    integration_code = """
# Integration with Swarm Middleware
import sys
sys.path.append('/home/k1/ccia_workspace/modules')
try:
    from swarm_middleware import process_task, save_successful_patch
    HAS_SWARM_MIDDLEWARE = True
except ImportError:
    HAS_SWARM_MIDDLEWARE = False
"""
    if "HAS_SWARM_MIDDLEWARE" not in content:
        content = integration_code + "\n" + content
        bridge_path.write_text(content, encoding="utf-8")
        print("✔ Enlace inyectado exitosamente en art_65_bridge.py")
    else:
        print("ℹ art_65_bridge.py ya cuenta con la importación del middleware.")
else:
    print("⚠ No se encontró art_65_bridge.py en el directorio de módulos.")
