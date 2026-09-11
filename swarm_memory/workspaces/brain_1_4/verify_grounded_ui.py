
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
