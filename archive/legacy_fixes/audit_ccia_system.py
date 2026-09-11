import os
import sys
import json
import sqlite3
import subprocess

print("=" * 80)
print("🔍 AUDITORÍA INTEGRAL DE INFRAESTRUCTURA Y AUTONOMÍA CCiA")
print("=" * 80)

# 1. Verificación de Autenticación GitHub CLI
print("\n[1/6] 🔑 Autenticación de GitHub CLI ('gh auth status'):")
try:
    res = subprocess.run(["/usr/bin/gh", "auth", "status"], capture_output=True, text=True, timeout=10)
    print(res.stdout if res.stdout else res.stderr)
except Exception as e:
    print(f"❌ Error consultando gh CLI: {e}")

# 2. Verificación de Estado de Ollama y Modelos
print("\n[2/6] 🧠 Modelos de Ollama disponibles:")
try:
    res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
    print(res.stdout.strip())
except Exception as e:
    print(f"❌ Error consultando Ollama: {e}")

# 3. Verificación de Podman y Aislamiento
print("\n[3/6] 📦 Sandbox de Podman:")
try:
    res = subprocess.run(["/usr/bin/podman", "run", "--rm", "alpine", "echo", "Podman Operativo OK"], capture_output=True, text=True, timeout=10)
    print(res.stdout.strip())
except Exception as e:
    print(f"⚠️ Podman test warning: {e}")

# 4. Verificación de SearXNG (Buscador Local)
print("\n[4/6] 🌐 Buscador Web SearXNG (http://127.0.0.1:8888):")
try:
    res = subprocess.run(["curl", "-s", "http://127.0.0.1:8888/search?q=test&format=json"], capture_output=True, text=True, timeout=5)
    if res.returncode == 0 and "results" in res.stdout:
        print("✅ SearXNG respondiendo correctamente en puerto 8888.")
    else:
        print("⚠️ SearXNG no responde en puerto 8888 (El sistema usará fallback automático a GitHub Code Search).")
except Exception as e:
    print(f"⚠️ SearXNG offline: {e}")

# 5. Verificación de Directorios de Memoria y Bases de Datos
print("\n[5/6] 💾 Estado de Bases de Datos y Memoria de Disco:")
paths = [
    "/home/k1/ccia_workspace/university.db",
    "/home/k1/ccia_workspace/swarm_memory/swarm_knowledge_base.db",
    "/home/k1/ccia_workspace/swarm_memory/genome_tree.db"
]
for p in paths:
    status = "✅ OK" if os.path.exists(p) else "❌ No existe"
    size = f"({os.path.getsize(p)} bytes)" if os.path.exists(p) else ""
    print(f"  • {p}: {status} {size}")

# 6. Prueba Final de Fitness de Artefacto 64
print("\n[6/6] 🧬 Verificación de Artefacto 64 (Evolutionary Compiler):")
try:
    sys.path.append('/home/k1/ccia_workspace')
    from modules.art_64 import Artefact64EvolutionaryCompiler
    res = Artefact64EvolutionaryCompiler.compile_and_test('audit_test.py', 'def test(): return True\n')
    print(f"  • Fitness Evaluado: {res['fitness']} (Esperado: 1.0)")
    print(f"  • Log: {res['log']}")
except Exception as e:
    print(f"❌ Error en prueba de Artefacto 64: {e}")

print("\n" + "=" * 80)
