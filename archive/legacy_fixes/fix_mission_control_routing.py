import os

mission_control_path = "/home/k1/ccia_mission_control.py"

if os.path.exists(mission_control_path):
    with open(mission_control_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Redirigir el artefacto 63 hacia ccia_mando_63.py en lugar de modules/art_63.py
    if "/home/k1/ccia_workspace/modules/art_63.py" in content:
        content = content.replace(
            "/home/k1/ccia_workspace/modules/art_63.py",
            "/home/k1/ccia_workspace/ccia_mando_63.py"
        )
    elif "modules/art_63.py" in content:
        content = content.replace("modules/art_63.py", "ccia_mando_63.py")
    else:
        # Reemplazo seguro de ruta de ejecución
        content = content.replace("art_63.py", "ccia_mando_63.py")
        
    with open(mission_control_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ ccia_mission_control.py actualizado: La Opción 4 del Artefacto 63 ahora abre el Centro de Mando interactivo (13 opciones).")
else:
    print("⚠️ No se encontró /home/k1/ccia_mission_control.py.")

