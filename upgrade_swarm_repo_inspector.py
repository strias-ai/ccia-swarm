import os
import sys
import json
import subprocess

print("=" * 80)
print("🛡️ INYECTANDO MAPEADOR DE REPOSITORIO Y FILTROS ANTI-ALUCINACIÓN")
print("=" * 80)

ws_dir = "/home/k1/ccia_workspace"

# 1. Crear el Módulo Mapeador de Código Fuente (repo_inspector.py)
inspector_code = '''import os

class RepoInspector:
    @staticmethod
    def build_repo_map(repo_dir, max_files=150):
        """Escanea el repositorio clonado y genera un mapa estructurado"""
        if not os.path.exists(repo_dir):
            return "⚠️ Error: El directorio del repositorio no existe."

        file_tree = []
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build'}

        for root, dirs, files in os.walk(repo_dir):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            rel_root = os.path.relpath(root, repo_dir)
            if rel_root == ".":
                rel_root = ""
            
            for f in files:
                rel_path = os.path.join(rel_root, f) if rel_root else f
                file_tree.append(rel_path)
                if len(file_tree) >= max_files:
                    break
            if len(file_tree) >= max_files:
                break

        tree_str = "\\n".join([f"  • {f}" for f in file_tree])
        return f"📂 ESTRUCTURA ACTUAL DEL REPOSITORIO ({len(file_tree)} archivos detectados):\\n{tree_str}"

    @staticmethod
    def read_key_files(repo_dir, file_list):
        """Lee el contenido de archivos clave dentro del repositorio"""
        contents = {}
        for rel_path in file_list:
            full_path = os.path.join(repo_dir, rel_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        contents[rel_path] = f.read()[:3000] # Límite por archivo
                except Exception as e:
                    contents[rel_path] = f"Error al leer: {e}"
        return contents
'''

inspector_path = os.path.join(ws_dir, "modules", "repo_inspector.py")
with open(inspector_path, "w", encoding="utf-8") as f:
    f.write(inspector_code)

print("  ✅ Módulo modules/repo_inspector.py creado con éxito.")

# 2. Inyectar Reglas Anti-Alucinación en modules/art_63.py
art63_path = os.path.join(ws_dir, "modules", "art_63.py")
with open(art63_path, "r", encoding="utf-8") as f:
    art63_code = f.read()

anti_hallucination_prompt = '''
# ==============================================================================
# 🎯 REGLAS ESTRICTAS ANTI-ALUCINACIÓN Y ANCLAJE DE REPOSITORIO
# ==============================================================================
STRICT_GROUNDING_SYSTEM_PROMPT = """
REGLAS OBLIGATORIAS E INVIOLABLES PARA EL ENJAMBRE:
1. NO analices badges, licencias ni el README a menos que el issue lo pida explícitamente.
2. Basate EXCLUSIVAMENTE en la estructura de archivos real del repositorio que se te proporciona.
3. Si la tarea pide crear rutas o código (ej. rutas de Next.js/React), DEBES generar los archivos completos y no dar consejos abstractos.
4. Cualquier propuesta de código DEBE ser enviada a la Sandbox para probar su compilación antes de responder.
5. Si falta contexto, indica los archivos específicos que necesitas leer en lugar de inventar parches genéricos.
"""
'''

if "STRICT_GROUNDING_SYSTEM_PROMPT" not in art63_code:
    art63_code = anti_hallucination_prompt + "\n\n" + art63_code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(art63_code)
    print("  ✅ Reglas de anclaje estricto inyectadas en modules/art_63.py.")

# Verificar sintaxis
subprocess.run([sys.executable, "-m", "py_compile", inspector_path], check=True)
subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)

print("=" * 80)
print("🚀 SISTEMA ACTUALIZADO CON ÉXITO: INSPECTOR DE REPOS + FILTROS ANTI-ALUCINACIÓN")
print("=" * 80)
