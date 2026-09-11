import os

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

        tree_str = "\n".join([f"  • {f}" for f in file_tree])
        return f"📂 ESTRUCTURA ACTUAL DEL REPOSITORIO ({len(file_tree)} archivos detectados):\n{tree_str}"

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
