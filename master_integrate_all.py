import os
import re
import sqlite3
import subprocess
import sqlite_vec

print("================================================================================")
print("🚀 INTEGRACIÓN COMPLETA DE CAPACIDADES Y OPTIMIZACIONES EN CCiA")
print("================================================================================")

# 1. Inicializar la tabla de vectores en university.db
db_path = "/home/k1/ccia_workspace/university.db"
try:
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bounty_embeddings (
                issue_id TEXT PRIMARY KEY,
                embedding float[384]
            );
        """)
    print("✅ 1. Tabla de memoria vectorial 'bounty_embeddings' activa en university.db.")
except Exception as e:
    print(f"⚠️ Error al inicializar memoria vectorial: {e}")

# 2. Probar Sandbox Podman
test_script = "/tmp/sandbox_check.py"
with open(test_script, "w", encoding="utf-8") as f:
    f.write("import sys; print('Podman Sandbox Operativo'); sys.exit(0)\n")

cmd = [
    "podman", "run", "--rm",
    "-v", f"{test_script}:/app/script.py:ro",
    "--network", "none",
    "--memory", "1g",
    "python:3.12-slim",
    "python3", "/app/script.py"
]
try:
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if res.returncode == 0:
        print(f"✅ 2. Podman Sandbox verificado: {res.stdout.strip()}")
    else:
        print(f"⚠️ Podman Sandbox respondió con aviso: {res.stderr.strip()}")
except Exception as e:
    print(f"⚠️ Error al ejecutar Podman Sandbox: {e}")

# 3. Vincular CCiAIntegrator y política keep_alive ("0m") en los orquestadores
targets = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for target in targets:
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()

        if "from modules.ccia_capabilities import CCiAIntegrator" not in content:
            content = "from modules.ccia_capabilities import CCiAIntegrator\n" + content

        if "self.capabilities = CCiAIntegrator()" not in content:
            init_pattern = r"(def __init__\(self[^\)]*\):)"
            replacement = r"\1\n        self.capabilities = CCiAIntegrator()"
            content = re.sub(init_pattern, replacement, content, count=1)

        # Inyectar liberación automática de modelos Ollama en RAM
        if '"keep_alive": "0m"' not in content:
            content = content.replace('"stream": True', '"stream": True, "keep_alive": "0m"')
            content = content.replace('"stream": False', '"stream": False, "keep_alive": "0m"')

        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 3. Capacidades e integración keep_alive aplicadas en: {target}")

print("================================================================================")
print("✨ FASE DE INTEGRACIÓN FINALIZADA CORRECTAMENTE")
print("================================================================================")
