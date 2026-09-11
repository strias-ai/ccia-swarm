import os
import re
import glob
import py_compile

print("=" * 80)
print("🔍 BUSCANDO TOKEN DE GITHUB Y REPARANDO SINTAXIS EN ARTEFACTO 63")
print("=" * 80)

# 1. Búsqueda exhaustiva del Token de GitHub
token = None

# Revisa variables de entorno activas
for k, v in os.environ.items():
    if ("GH" in k or "TOKEN" in k or "GITHUB" in k) and isinstance(v, str):
        if v.startswith("ghp_") or v.startswith("github_pat_"):
            token = v
            print(f"  ✅ Token encontrado en la variable de entorno: {k}")
            break

# Revisa archivos de configuración y registros si no se halló en entorno
if not token:
    search_patterns = [
        "/home/k1/ccia_workspace/.env*",
        "/home/k1/ccia_workspace/*.json",
        "/home/k1/ccia_workspace/*.log",
        "/home/k1/ccia_workspace/*.sh",
        "/home/k1/.bashrc",
        "/home/k1/.gitconfig",
        "/home/k1/.config/gh/hosts.yml"
    ]
    for pattern in search_patterns:
        for filepath in glob.glob(pattern):
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        match = re.search(r'(ghp_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,})', text)
                        if match:
                            token = match.group(1)
                            print(f"  ✅ Token localizado dentro de: {filepath}")
                            break
                except Exception:
                    pass
        if token:
            break

# Inyectar el token encontrado en .env
env_file = "/home/k1/ccia_workspace/.env"
if token:
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            env_lines = f.readlines()
    
    # Remover entradas previas
    env_lines = [l for l in env_lines if not l.startswith("GITHUB_TOKEN=") and not l.startswith("GH_PAT=")]
    env_lines.append(f"GITHUB_TOKEN={token}\n")
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(env_lines)
    
    masked = token[:4] + "..." + token[-4:] if len(token) > 8 else "***"
    print(f"  🚀 GITHUB_TOKEN [{masked}] guardado exitosamente en {env_file}")
else:
    print("  ⚠️ No se encontró la cadena del token ghp_ en los archivos escaneados.")

# 2. Corrección del IndentationError en la línea 1 de art_63.py
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Eliminar líneas vacías al inicio y limpiar sangría de la primera línea de código
fixed_lines = []
file_started = False

for line in lines:
    if not file_started:
        if line.strip():
            file_started = True
            fixed_lines.append(line.lstrip())  # Quita sangría inesperada en línea 1
        else:
            continue
    else:
        fixed_lines.append(line)

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print("\n🛠️ VERIFICACIÓN DE COMPILACIÓN:")
try:
    py_compile.compile(art63_path, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: modules/art_63.py está listo sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación residual:\n{e}")

print("=" * 80)
