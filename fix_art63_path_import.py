import os

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

if os.path.exists(art63_path):
    with open(art63_path, "r", encoding="utf-8") as f:
        content = f.read()

    sys_path_fix = """import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
"""

    if "BASE_DIR = os.path.dirname" not in content:
        content = sys_path_fix + "\n" + content
        with open(art63_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Fix de PYTHONPATH inyectado en modules/art_63.py")
    else:
        print("ℹ️ modules/art_63.py ya contiene la resolución de ruta.")
else:
    print("⚠️ No se encontró el archivo modules/art_63.py.")
