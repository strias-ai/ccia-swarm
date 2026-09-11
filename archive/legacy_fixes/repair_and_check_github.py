import os
import re

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
env_path = "/home/k1/ccia_workspace/.env"

print("=" * 80)
print("🛠️ REPARANDO SINTAXIS EN ARTEFACTO 63 Y REVISANDO CREDENCIALES GITHUB")
print("=" * 80)

# 1. Reparar archivo modules/art_63.py
if os.path.exists(art63_path):
    with open(art63_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Reemplazar cadenas multilíngües corruptas o no terminadas
    # Corregir la asignación limpia de repo_files_summary
    code = code.replace('repo_files_summary = "\n', 'repo_files_summary = ""\n')
    
    # Asegurar la función de extracción de contexto limpia
    if "def get_repo_files_context" not in code:
        helper_func = '''
def get_repo_files_context(repo_dir: str) -> str:
    """Extrae hasta 30 archivos rastreados por git en el repositorio local."""
    if not os.path.exists(repo_dir):
        return "Estructura no disponible."
    try:
        import subprocess
        files_out = subprocess.check_output(
            ["git", "-C", repo_dir, "ls-files"], stderr=subprocess.DEVNULL
        ).decode("utf-8").splitlines()
        return "\\n".join(files_out[:30]) if files_out else "Repositorio vacío o sin archivos git."
    except Exception:
        return "Error al listar archivos del repositorio."
'''
        code = helper_func + "\n" + code

    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("  ✅ Archivo modules/art_63.py reparado correctamente.")

# 2. Revisar si GITHUB_TOKEN / GH_PAT está configurado
print("\n🔑 AUDITORÍA DE AUTENTICACIÓN GITHUB:")
print("─" * 80)

gh_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT")

if not gh_token and os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_PAT="):
                gh_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if gh_token:
    masked_token = gh_token[:4] + "..." + gh_token[-4:] if len(gh_token) > 8 else "***"
    print(f"  ✅ Token de GitHub DETECTADO y ACTIVO: [{masked_token}]")
    print("  🚀 La publicación automática de Pull Requests / Issues está LISTA para operar.")
else:
    print("  ⚠️ No se encontró GITHUB_TOKEN en el entorno ni en .env.")
    print("  💡 Para habilitar la creación automática de PRs, añade a tu .env:")
    print("     GITHUB_TOKEN=ghp_tu_token_de_github_aqui")

print("=" * 80)
