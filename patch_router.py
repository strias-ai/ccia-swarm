import sqlite3

# Actualización de la Core API para importar endpoints monetizadores
core_api_path = "/home/k1/ccia_workspace/ccia_core_api.py"

with open(core_api_path, "r") as f:
    content = f.read()

if "include_router" not in content:
    print("Patching ccia_core_api.py para incluir enrutamiento unificado...")
    patch = """
# Routers unificados de Vectores Monetizadores
from modules.github_fix_bot import router as fix_bot_router
from modules.synthetic_data_api import router as datasets_router
from modules.a2a_escrow_engine import router as escrow_router

app.include_router(fix_bot_router, prefix="/v1/fix-bot", tags=["Vector 3: Fix-Bot"])
app.include_router(datasets_router, prefix="/v1/datasets", tags=["Vector 4: Datasets"])
app.include_router(escrow_router, prefix="/v1/a2a", tags=["Vector 6: A2A Escrow"])
"""
    with open(core_api_path, "a") as f:
        f.write(patch)
    print("🟢 Parche aplicado con éxito.")
else:
    print("🟢 Enrutamiento ya configurado previamente.")
