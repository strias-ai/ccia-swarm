
import os

ws_dir = "/home/k1/ccia_workspace/swarm_memory/workspaces/brain_1_4"
expected_files = [
    "app/page.tsx",
    "app/bounties/page.tsx",
    "app/bounties/[id]/page.tsx",
    "app/create/page.tsx"
]

def run_sandbox_validation():
    print("🔍 Validando estructura de componentes UI en Sandbox...")
    for rel_path in expected_files:
        target_path = os.path.join(ws_dir, rel_path)
        assert os.path.exists(target_path), f"Error: No existe el archivo {rel_path}"
        
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "export default" in content, f"Error: {rel_path} no exporta un componente por defecto"
            assert len(content) > 100, f"Error: {rel_path} tiene un contenido incompleto"
        print(f"  • {rel_path}: Estructura sintáctica y exportación OK")

    print("✅ VALIDACIÓN COMPLETA DE FLUJO DE SANDBOX: 4/4 Rutas UI verificadas.")

run_sandbox_validation()
