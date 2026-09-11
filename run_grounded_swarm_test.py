import sys
import os

sys.path.append('/home/k1/ccia_workspace')
from modules.repo_inspector import RepoInspector
from modules.art_63 import EmpiricalBrainBridge

# 1. Definir la ruta del proyecto objetivo
target_repo_dir = "/home/k1/ccia_workspace/swarm_memory/workspaces/brain_1_4"

# 2. Generar inspección de código
repo_map = RepoInspector.build_repo_map(target_repo_dir)

print("=" * 80)
print("🔍 REPO MAPPER INYECTADO AL CONTEXTO DEL ENJAMBRE:")
print("=" * 80)
print(repo_map)
print("=" * 80)

# 3. Ejecutar prueba de verificación en la Sandbox de Artefacto 64
test_script = """
import os

routes = ['app/page.tsx', 'app/bounties/page.tsx', 'app/bounties/[id]/page.tsx', 'app/create/page.tsx']
base_dir = '/home/k1/ccia_workspace/swarm_memory/workspaces/brain_1_4'

missing = []
for r in routes:
    path = os.path.join(base_dir, r)
    if not os.path.exists(path):
        missing.append(r)

if missing:
    print(f'❌ Rutas faltantes: {missing}')
    exit(1)

print('✅ Las 4 rutas de la UI existen y están correctamente ubicadas en la estructura Next.js App Router.')
"""

res = EmpiricalBrainBridge.execute_in_sandbox("1.4", "verify_grounded_ui.py", test_script)

print("\n" + "=" * 80)
print("🧪 EVALUACIÓN EMPÍRICA DE LA QUEEN SANDBOX GATE")
print("=" * 80)
print(f"• Fitness Score: {res.get('fitness', 0.0)}")
print(f"• Resultado:\n{res.get('log', '')}")
print("=" * 80)
