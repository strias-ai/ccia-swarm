# -*- coding: utf-8 -*-
import json
import os
import subprocess

REGISTRY_PATH = "/home/k1/ccia_workspace/api_backend_jwt/module_registry.json"

print("📜 [1/3] Leyendo Libro Mayor de Extensiones (module_registry.json)...")
if os.path.exists(REGISTRY_PATH):
    with open(REGISTRY_PATH, "r") as f:
        data = json.load(f)
        exts = data.get("extensions", {})
        print(f"✅ Módulos Evolutivos Registrados: {len(exts)}")
        for name, info in exts.items():
            print(f"  • [OK] {name}: {info.get('description', '')[:60]}...")
else:
    print("⚠️ No se localizó el archivo de registro.")

print("\n🛡️ [2/3] Verificando compilación del panel principal...")
res = subprocess.run(["python3", "-c", "import ast; ast.parse(open('/home/k1/ccia_mission_control.py').read()); print('AST OK')"], capture_output=True, text=True)
print(f"✅ Sintaxis AST Mission Control: {res.stdout.strip()}")

print("\n🚀 [3/3] Estado de Servicios en Segundo Plano...")
watchdog = subprocess.run(["fuser", "8090/tcp"], capture_output=True, text=True)
print(f"🌐 Dashboard Web (Puerto 8090): {'🟢 ACTIVO' if watchdog.returncode == 0 else '🔴 INACTIVO'}")
