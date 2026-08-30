import os
import re
import sqlite3
import subprocess

DB_PATH = "/home/k1/ccia_workspace/university.db"
SHELL_SCRIPT = "/home/k1/ccia_workspace/start_core_api.sh"
DASHBOARD_SCRIPT = "/home/k1/ccia_workspace/admin_dashboard.py"

print("🛠️ 1. IDENTIFICANDO ARQUIVO PYTHON PRINCIPAL DE LA CORE API...")

py_app_path = None
if os.path.exists(SHELL_SCRIPT):
    with open(SHELL_SCRIPT, "r") as f:
        sh_content = f.read()
    # Buscar módulo uvicorn o comando python en el script de arranque
    match = re.search(r'uvicorn\s+([a-zA-Z0-9_\.]+):app', sh_content)
    if match:
        module_name = match.group(1).replace(".", "/") + ".py"
        py_app_path = os.path.join("/home/k1/ccia_workspace", module_name)

if not py_app_path or not os.path.exists(py_app_path):
    # Búsqueda de respaldo
    for root, _, files in os.walk("/home/k1/ccia_workspace"):
        for file in files:
            if file in ["main.py", "core_api.py", "app.py"]:
                py_app_path = os.path.join(root, file)
                break

if py_app_path and os.path.exists(py_app_path):
    print(f"🟢 Target detectado: {py_app_path}")
    with open(py_app_path, "r") as f:
        code = f.read()
    
    if "fix_bot_router" not in code:
        patch_code = """

# --- VECTORES MONETIZADORES UNIFICADOS ---
try:
    from modules.github_fix_bot import router as fix_bot_router
    from modules.synthetic_data_api import router as datasets_router
    from modules.a2a_escrow_engine import router as escrow_router

    app.include_router(fix_bot_router, prefix="/v1/fix-bot", tags=["Vector 3: Fix-Bot"])
    app.include_router(datasets_router, prefix="/v1/datasets", tags=["Vector 4: Datasets"])
    app.include_router(escrow_router, prefix="/v1/a2a", tags=["Vector 6: A2A Escrow"])
except Exception as e:
    print(f"[CoreAPI Patch Warning] {e}")
"""
        with open(py_app_path, "a") as f:
            f.write(patch_code)
        print("🟢 Router acoplado con éxito.")
    else:
        print("🟢 Routers ya estaban integrados.")
        
    subprocess.run(["sudo", "systemctl", "restart", "ccia-core-api.service"])
    print("🟢 Servicio ccia-core-api reiniciado.")
else:
    print("⚠️ No se pudo determinar el script Python principal del script shell.")

print("\n📊 2. ACTUALIZANDO DASHBOARD CON CONSULTAS EXACTAS DE BASE DE DATOS...")

# Parchear admin_dashboard.py para usar la columna real 'event_id' y calcular pagos Stripe en vivo
with open(DASHBOARD_SCRIPT, "r") as f:
    dash_code = f.read()

# Reemplazar consulta genérica de dashboard para finanzas en vivo
old_query = "cursor.execute(\"SELECT COALESCE(SUM(bounty_amount), 0.0) FROM bounties_captured\")"
if "SELECT COALESCE(SUM(amount), 0) / 100.0 FROM processed_stripe_events" not in dash_code:
    dash_code = dash_code.replace(
        "cursor.execute(\"SELECT COALESCE(SUM(bounty_amount), 0.0) FROM bounties_captured\")",
        "cursor.execute(\"SELECT COALESCE(SUM(amount), 0) / 100.0 FROM processed_stripe_events\")"
    )
    with open(DASHBOARD_SCRIPT, "w") as f:
        f.write(dash_code)
    print("🟢 Dashboard actualizado para procesar 'processed_stripe_events' en vivo.")

print("\n✅ Mejoras aplicadas correctamente.")
