import socket
import subprocess
import json

print("=" * 80)
print("🔌 REVISIÓN DE PUERTOS ACTIVOS Y SERVICIOS CCiA")
print("=" * 80)

# 1. Escaneo de Puertos Locales Clave
target_ports = {
    11434: "Ollama LLM Engine",
    8888: "SearXNG Web Search",
    8080: "Proxy / Alt HTTP",
    5000: "Flask / API Service",
    3000: "Web Dashboard / Frontend",
    5432: "PostgreSQL DB",
    6379: "Redis Cache"
}

print("\n1. 📡 Estado de Puertos Locales:")
for port, name in target_ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    status = "🟢 ABIERTO / EN ESCUCHA" if result == 0 else "🔴 CERRADO"
    print(f"  • Puerto {port:<5} ({name}): {status}")

# 2. Revisión de Contenedores de Podman / Docker
print("\n2. 📦 Contenedores activos en Podman:")
try:
    res = subprocess.run(["/usr/bin/podman", "ps", "-a", "--format", "json"], capture_output=True, text=True, timeout=5)
    if res.returncode == 0 and res.stdout.strip():
        containers = json.loads(res.stdout)
        if containers:
            for c in containers:
                names = c.get("Names", ["desconocido"])
                status = c.get("State", c.get("Status", "N/A"))
                image = c.get("Image", "N/A")
                ports = c.get("Ports", [])
                print(f"  • Contenedor: {names} | Estado: {status} | Imagen: {image}")
        else:
            print("  ⚠️ No hay contenedores ejecutándose en Podman actualmente.")
    else:
        print("  ⚠️ No se detectaron contenedores activos.")
except Exception as e:
    print(f"  ❌ Error consultando Podman: {e}")

# 3. Diagnóstico de enchufes activos en el sistema (ss)
print("\n3. 🖥️ Todos los puertos TCP en escucha en el sistema (ss -tulpn):")
try:
    res_ss = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, timeout=5)
    lines = res_ss.stdout.splitlines()
    for line in lines[:15]: # Mostrar los primeros 15 puertos
        print(f"  {line}")
except Exception as e:
    print(f"  ❌ Error ejecutando ss: {e}")

print("\n" + "=" * 80)
