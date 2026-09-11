import re
import os

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

print("=" * 80)
print("🛠️ VINCULANDO CONTEXTO DE GIT Y HOOK DE STREAMING EN ARTEFACTO 63")
print("=" * 80)

# 1. Modificar la construcción de prompt para incluir issue.body y el árbol de archivos git
old_prompt_pattern = r'prompt\s*=\s*f"""([^"]*)"""'

enhanced_prompt_logic = '''
        # Extracción de contexto real del repositorio
        repo_files_summary = ""
        if os.path.exists(repo_dir):
            try:
                import subprocess
                files_out = subprocess.check_output(
                    ["git", "-C", repo_dir, "ls-files"], stderr=subprocess.DEVNULL
                ).decode("utf-8").splitlines()
                repo_files_summary = "\\n".join(files_out[:30])
            except Exception:
                repo_files_summary = "No se pudo listar la estructura de archivos."

        prompt = f"""Ubicación Repositorio: {repo_url}
Issue Título: {issue_title}
Cuerpo del Issue / Descripción: {issue_body if 'issue_body' in locals() and issue_body else 'Sin descripción extendida'}

Estructura de Archivos en el Repositorio (Primeros 30 archivos):
{repo_files_summary}

Rol Asignado: {brain_role}
Analiza el código y proporciona el dictamen o parche técnico correspondiente."""
'''

if "repo_files_summary" not in code:
    # Buscar el punto donde se invoca la inferencia de cada cerebro y reemplazar la asignación del prompt
    code = re.sub(r'prompt\s*=\s*f""".*?"""', enhanced_prompt_logic, code, flags=re.DOTALL)
    print("  ✅ [1/2] Inyección de contexto real de Git (issue body + árbol de archivos) agregada.")

# 2. Reemplazar expresiones print directas con limpieza de <think>
if "re.sub(r'<think>.*?</think>', '', chunk" not in code:
    code = code.replace(
        'sys.stdout.write(chunk)',
        'clean_chunk = re.sub(r"<think>.*?</think>", "", chunk, flags=re.DOTALL)\n            sys.stdout.write(clean_chunk)'
    )
    print("  ✅ [2/2] Hook de limpieza en tiempo real para stdout aplicado.")

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("=" * 80)
print("🚀 MÓDULO ARTEFACTO 63 ACTUALIZADO")
print("=" * 80)
