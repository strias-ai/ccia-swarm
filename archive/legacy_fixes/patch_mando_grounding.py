import os

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inyección del Inspector de Repositorio en la fase de clonación/lectura
    if "RepoInspector.build_repo_map" not in content:
        import_line = "from modules.repo_inspector import RepoInspector\n"
        content = import_line + content
        
        # Guardar cambios
        with open(mando_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ ccia_mando_63.py parcheado exitosamente con RepoInspector.")
else:
    print("⚠️ No se encontró ccia_mando_63.py para parchear.")
