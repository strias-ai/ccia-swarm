#!/usr/bin/env python3
import os, subprocess, shutil, urllib.request, json

def check(title, cmd):
    print(f"\n=== 🔍 {title} ===")
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        print(res.stdout.strip() if res.stdout.strip() else res.stderr.strip() if res.stderr.strip() else "OK (Sin salida)")
    except Exception as e:
        print(f"⚠️ Error al ejecutar: {e}")

print("==================================================")
print("🛡️ DIAGNÓSTICO INTEGRAL DE RECURSOS CCIA2 / SISTEMA")
print("==================================================")

# 1. Memoria RAM y Swap
check("MEMORIA RAM Y SWAP", "free -h")

# 2. Espacio en Disco
check("ESPACIO EN DISCO (Almacenamiento)", "df -h / /home")

# 3. Estado de GPU AMD / ROCm
check("ACELERACIÓN AMD ROCm / GPU", "rocm-smi || clinfo | grep -i 'Device Name' || ls -la /dev/kfd /dev/dri 2>/dev/null")

# 4. Ollama LLM Local Status
print("\n=== 🤖 ESTADO DE OLLAMA (Local LLM Server) ===")
try:
    req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
    data = json.loads(req.read().decode())
    models = [m['name'] for m in data.get('models', [])]
    print(f"✅ Ollama Servicio Activo. Modelos listos ({len(models)}): {', '.join(models) if models else 'Ninguno cargado'}")
except Exception as e:
    print(f"❌ Ollama no responde en http://localhost:11434: {e}")

# 5. Puertos HTTP y Servicios de Red Escuchando
check("PUERTOS HTTP / SERVICIOS ACTIVOS", "ss -tlpn | grep -E 'LISTEN'")

# 6. Proceso con consumo excesivo de CPU (Top 5)
check("TOP 5 PROCESOS POR CONSUMO DE CPU", "ps aux --sort=-%cpu | head -n 6")

print("\n==================================================")
