import os
import re

print("=" * 80)
print("🔍 AUDITORÍA DE ORQUESTACIÓN DE OLLAMA Y SCHEDULERS (CCiA)")
print("=" * 80)

modules_dir = "/home/k1/ccia_workspace/modules"
root_dir = "/home/k1/ccia_workspace"

artifacts_to_check = {
    "Artefacto 28 (Chronos Scheduler)": ["chronos_scheduler.py", "art_28.py"],
    "Artefacto 59 (Email Dispatcher)": ["art_59.py"],
    "Artefacto 60 (CRM & Dual-Brain)": ["art_60.py"],
    "Artefacto 61 (Ollama Scheduler)": ["art_61.py"],
    "Artefacto 62 (Pro-Bono Multi-Agent)": ["art_62.py"],
    "Artefacto 63 (Tri-Swarm Bounties)": ["art_63.py"]
}

for name, files in artifacts_to_check.items():
    print(f"\n📦 {name}:")
    found = False
    for fname in files:
        paths = [
            os.path.join(modules_dir, fname),
            os.path.join(root_dir, fname)
        ]
        for p in paths:
            if os.path.exists(p):
                found = True
                print(f"  📄 Archivo localizado: {p}")
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        
                        ollama_calls = re.findall(r'http://[^\s\'"]+:11434[^\s\'"]*', code)
                        models_used = re.findall(r'["\']model["\']\s*:\s*["\']([^"\'\n]+)["\']', code)
                        keep_alives = re.findall(r'["\']keep_alive["\']\s*:\s*([^,\}\n]+)', code)
                        streams = re.findall(r'["\']stream["\']\s*:\s*([^,\}\n]+)', code)
                        
                        print(f"     - Endpoints Ollama : {set(ollama_calls) if ollama_calls else 'Uso dinámico/Librería'}")
                        print(f"     - Modelos en código: {set(models_used) if models_used else 'Detección por variables'}")
                        print(f"     - Ajustes keep_alive: {set(keep_alives) if keep_alives else 'Defecto (5m)'}")
                        print(f"     - Streaming activo : {set(streams) if streams else 'Falso / No especificado'}")
                except Exception as e:
                    print(f"     ⚠️ Error en lectura: {e}")
    if not found:
        print("  ⚠️ No localizado en la ruta habitual.")

print("\n" + "=" * 80)
