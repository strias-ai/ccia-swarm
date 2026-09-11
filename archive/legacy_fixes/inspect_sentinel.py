import subprocess

print("================================================================================")
print("🔍 REVISIÓN DE SENTINEL_TUNNEL_GUARD.PY (ARTEFACTO 39)")
print("================================================================================")

path = "/home/k1/ccia_workspace/modules/sentinel_tunnel_guard.py"
try:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"📏 Tamaño del archivo: {len(content)} bytes\n")
        print("📄 PRIMERAS 40 LÍNEAS:")
        print("\n".join(content.splitlines()[:40]))
except Exception as e:
    print(f"❌ Error al leer {path}: {e}")

print("================================================================================")
