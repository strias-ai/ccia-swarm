import os
import re

print("================================================================================")
print("🔧 CORRECCIÓN ARQUITECTÓNICA DE ENRUTAMIENTO (ARTEFACTO 63)")
print("================================================================================")

mc_path = "/home/k1/ccia_mission_control.py"
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

# 1. Parche en ccia_mission_control.py para enrutamiento dinámico (art_num == 63)
if os.path.exists(mc_path):
    with open(mc_path, "r", encoding="utf-8") as f:
        mc_code = f.read()

    # Inyección para interceptar la Opción 4 del Artefacto 63 específicamente
    if "ccia_mando_63.py" not in mc_code:
        pattern = r'(def artifact_sub_menu\(art_num\):)'
        replacement = r'\1\n    if str(art_num) in ["63", "63.0"]:\n        import subprocess, sys\n        subprocess.run([sys.executable, "/home/k1/ccia_workspace/ccia_mando_63.py"])\n        return'
        mc_code = re.sub(pattern, replacement, mc_code, count=1)
        with open(mc_path, "w", encoding="utf-8") as f:
            f.write(mc_code)
        print("  ✅ ccia_mission_control.py: Intercepción explícita inyectada para Artefacto 63.")
    else:
        print("  ℹ️ ccia_mission_control.py ya contiene la referencia al centro de mando.")

# 2. Capa de Seguridad en modules/art_63.py: Redirigir __main__ al Centro de Mando
if os.path.exists(art63_path):
    with open(art63_path, "r", encoding="utf-8") as f:
        art_code = f.read()

    # Sustituir la ejecución automática por la apertura del Centro de Mando de 13 opciones
    new_main = """if __name__ == "__main__":
    import subprocess
    import sys
    mando_script = "/home/k1/ccia_workspace/ccia_mando_63.py"
    if os.path.exists(mando_script):
        subprocess.run([sys.executable, mando_script])
    else:
        orchestrator = TriSwarmOrchestrator()
        orchestrator.run_full_pipeline()"""

    if 'orchestrator.run_full_pipeline()' in art_code and 'mando_script' not in art_code:
        pattern_main = r'if __name__ == "__main__":.*'
        art_code = re.sub(pattern_main, new_main, art_code, flags=re.DOTALL)
        with open(art63_path, "w", encoding="utf-8") as f:
            f.write(art_code)
        print("  ✅ modules/art_63.py: Bloque __main__ reconfigurado para invocar ccia_mando_63.py.")
    else:
        print("  ℹ️ modules/art_63.py ya cuenta con la capa de redirección.")

