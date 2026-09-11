import sqlite3
import os
import re

DB_PATH = "/home/k1/ccia_workspace/ccia_bounties.db"
ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"

print("=" * 80)
print("🛠️ SANEAMIENTO DE ARTEFACTO 63: CONTEXTO DE CÓDIGO Y AUDITORÍA DB")
print("=" * 80)

# 1. Auditoría de tablas reales en DB
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  ✅ Tablas encontradas en ccia_bounties.db: {tables}")
    conn.close()
else:
    print("  ⚠️ DB no encontrada en la ruta especificada.")

# 2. Inyección de Contexto de Código Real en art_63.py
if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    # Función inyectable para leer la estructura de código del repo clonado
    context_injector = '''
def build_repo_context(repo_dir):
    """Extrae el árbol de archivos y snippets clave del repo clonado."""
    if not repo_dir or not os.path.exists(repo_dir):
        return "No hay repositorio clonado disponible."
    
    context = []
    context.append("=== ESTRUCTURA DE ARCHIVOS DEL REPOSITORIO ===")
    file_count = 0
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo_dir)
            context.append(f"- {rel_path}")
            file_count += 1
            if file_count > 40:
                break
        if file_count > 40:
            break

    context.append("\\n=== CONTENIDO DE ARCHIVOS CLAVE ===")
    key_files = ['README.md', 'main.py', 'package.json', 'Cargo.toml', 'requirements.txt', 'go.mod']
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if f in key_files or f.endswith(('.py', '.rs', '.go', '.js', '.sol')):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, repo_dir)
                try:
                    with open(full_p, 'r', encoding='utf-8', errors='ignore') as c_file:
                        content = c_file.read(1500) # Primeros 1500 caracteres
                        context.append(f"--- INICIO ARCHIVO: {rel_p} ---\\n{content}\\n--- FIN ARCHIVO ---")
                except Exception:
                    pass
                if len(context) > 10:
                    break
    return "\\n".join(context)
'''

    if "def build_repo_context" not in code:
        code = context_injector + "\n\n" + code
        print("  ✅ Módulo de lectura de contexto de archivos inyectado en art_63.py.")

    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.write(code)
else:
    print("  ❌ No se encontró art_63.py")

print("=" * 80)
