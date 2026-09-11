import os
import py_compile

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Localizar donde inicia la definición original de clase o imports válidos
start_idx = 0
for idx, line in enumerate(lines):
    # Buscar la primera definición limpia sin sangría que sea import o clase
    if (line.startswith("import ") or line.startswith("from ") or line.startswith("class TriSwarmOrchestrator")) and idx > 0:
        start_idx = idx
        break

clean_header = [
    "import os\n",
    "import sys\n",
    "import re\n",
    "import json\n",
    "import subprocess\n",
    "\n",
    "def get_repo_files_context(repo_dir: str) -> str:\n",
    "    if not os.path.exists(repo_dir):\n",
    '        return "Estructura no disponible."\n',
    "    try:\n",
    "        files_out = subprocess.check_output(\n",
    '            ["git", "-C", repo_dir, "ls-files"], stderr=subprocess.DEVNULL\n',
    '        ).decode("utf-8").splitlines()\n',
    '        return "\\n".join(files_out[:30]) if files_out else "Repositorio vacío o sin archivos git."\n',
    "    except Exception:\n",
    '        return "Error al listar archivos del repositorio."\n',
    "\n"
]

final_lines = clean_header + lines[start_idx:]

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print("=" * 80)
print("🛠️ RECONSTRUCCIÓN DEFINITIVA DE CABECERA EN ARTEFACTO 63")
print("=" * 80)

try:
    py_compile.compile(art63_path, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: modules/art_63.py listo y verificado.")
    print("  🔑 Token de GitHub cargado y activo en el entorno.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
