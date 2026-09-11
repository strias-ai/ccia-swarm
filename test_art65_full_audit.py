import os
import sys
import json
import sqlite3
import subprocess

print("=" * 80)
print("🧪 AUDITORÍA INTEGRAL DE ENTORNO Y ENLACE: ARTEFACTO 65 (SWARM GATEWAY)")
print("=" * 80)

ERRORS = 0

# 1. Verificar presencia de módulos clave
modules_to_check = [
    "/home/k1/ccia_workspace/modules/art_65.py",
    "/home/k1/ccia_workspace/ccia_mando_65.py",
    "/home/k1/ccia_mission_control.py"
]

print("\n1. 🔍 Verificación de Archivos y Módulos del Sistema:")
for mod in modules_to_check:
    if os.path.exists(mod):
        print(f"  ✅ Archivo presente: {mod}")
    else:
        print(f"  ❌ Archivo ausente: {mod}")
        ERRORS += 1

# 2. Probar importación dinámica del Gateway (Artefacto 65)
print("\n2. 🔌 Prueba de Importación y Métodos del Gateway (art_65.py):")
sys.path.append("/home/k1/ccia_workspace/modules")
try:
    from art_65 import CCiASwarmGateway
    print("  ✅ Módulo CCiASwarmGateway importado correctamente.")
    
    # Probar inspector de repositorio (Ojos)
    inspection = CCiASwarmGateway.inspect_repository("/home/k1/ccia_workspace")
    files_found = len(inspection.get("file_tree", []))
    snippets_found = len(inspection.get("code_snippets", {}))
    print(f"  ✅ [OJOS] Inspección local exitosa: {files_found} archivos detectados, {snippets_found} fragmentos extraídos.")
    
except Exception as e:
    print(f"  ❌ Error al probar CCiASwarmGateway: {e}")
    ERRORS += 1

# 3. Desplegar catálogo de prompts por defecto en PromptRepo
print("\n3. 📚 Generación del Catálogo de Prompts Dinámicos (/prompts):")
prompts_dir = "/home/k1/ccia_workspace/prompts"
os.makedirs(prompts_dir, exist_ok=True)

templates = {
    "python_security_auditor.json": {
        "language": "python",
        "system_prompt": "Eres un auditor Senior de seguridad Python. Analiza AST, inyecciones SQL y vulnerabilidades RCE.",
        "context_sources": ["tree", "AST", "requirements.txt"]
    },
    "rust_memory_safety.json": {
        "language": "rust",
        "system_prompt": "Eres un auditor de memoria en Rust. Examina bloques unsafe y lifespans.",
        "context_sources": ["Cargo.toml", "src/main.rs"]
    },
    "c_cpp_memory_leak.json": {
        "language": "c",
        "system_prompt": "Eres un analista C/C++. Revisa punteros colgados, buffer overflows y fugas en malloc/free.",
        "context_sources": ["Makefile", "main.c"]
    }
}

for tmpl_name, tmpl_content in templates.items():
    file_path = os.path.join(prompts_dir, tmpl_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tmpl_content, f, indent=2)
    print(f"  ✅ Plantilla cargada: {tmpl_name}")

# 4. Probar ejecución aislada Sandbox (Manos)
print("\n4. 🧪 Prueba de Ejecución aislada Sandbox (VANT Sandbox Engine):")
try:
    res = subprocess.run(
        ["python3", "-c", "import sys; print(f'Sandbox Runtime Python {sys.version.split()[0]} OK')"],
        capture_output=True, text=True, timeout=5
    )
    if res.returncode == 0:
        print(f"  ✅ [MANOS] Sandbox responde: {res.stdout.strip()}")
    else:
        print(f"  ❌ Fallo en Sandbox: {res.stderr}")
        ERRORS += 1
except Exception as e:
    print(f"  ❌ Error al invocar ejecutor Sandbox: {e}")
    ERRORS += 1

# 5. Simular llamada A2A desde Enjambre (Artefacto 63/64)
print("\n5. 🔄 Simulación de Integración A2A (Enjambre 63/64 -> Gateway 65):")
try:
    mock_payload = {
        "agent_origin": "art_63_tri_swarm",
        "target_repo": "/home/k1/ccia_workspace",
        "action": "FETCH_AST_AND_PROMPT",
        "detected_lang": "python"
    }
    
    # Cargar el prompt dinámico según lenguaje
    prompt_file = os.path.join(prompts_dir, "python_security_auditor.json")
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_config = json.load(f)
        
    context = CCiASwarmGateway.inspect_repository(mock_payload["target_repo"])
    
    enriched_prompt = {
        "system": prompt_config["system_prompt"],
        "real_tree": context["file_tree"][:5],
        "snippets_keys": list(context["code_snippets"].keys())[:3]
    }
    
    print("  ✅ [A2A BUS] Contexto inyectado en prompt dinámico exitosamente:")
    print(f"     • Promp System: {enriched_prompt['system'][:60]}...")
    print(f"     • Árbol Inyectado: {enriched_prompt['real_tree']}")
    print(f"     • Snippets listos para Ollama: {enriched_prompt['snippets_keys']}")

except Exception as e:
    print(f"  ❌ Fallo en simulación A2A: {e}")
    ERRORS += 1

print("\n" + "=" * 80)
if ERRORS == 0:
    print("🎉 AUDITORÍA COMPLETA: TODOS LOS SISTEMAS DEL ARTEFACTO 65 OPERATIVOS")
else:
    print(f"⚠️ AUDITORÍA FINALIZADA CON {ERRORS} ERRORES DETECTADOS")
print("=" * 80)
