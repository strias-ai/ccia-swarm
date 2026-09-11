import os

target_files = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

path_fix = """import sys, os
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if os.path.basename(os.path.dirname(__file__)) == "modules" else os.path.abspath(os.path.dirname(__file__))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)
"""

for filepath in target_files:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "WORKSPACE_DIR" not in content:
            new_content = path_fix + "\n" + content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ sys.path ajustado correctamente en: {filepath}")
        else:
            print(f"ℹ️ sys.path ya estaba configurado en: {filepath}")

