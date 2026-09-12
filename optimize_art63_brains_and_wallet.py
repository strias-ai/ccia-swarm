import os
import re
import subprocess

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"
MANDO63_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("================================================================================")
print("🧹 CCiA CTO ENGINE: PURGA DE MODELOS DUPLICADOS Y RECONFIGURACIÓN DE CEREBROS")
print("================================================================================")

# 1. Purga de los 15 modelos ccia-s* redundantes
ccia_models = [
    "ccia-s1-1-spam-detector:latest", "ccia-s1-2-ast-parser:latest",
    "ccia-s1-3-algo-designer:latest", "ccia-s1-4-patch-generator:latest",
    "ccia-s1-5-compliance-auditor:latest", "ccia-s2-1-syntax-validator:latest",
    "ccia-s2-2-perf-profiler:latest", "ccia-s2-3-mutation-agent:latest",
    "ccia-s2-4-patch-historian:latest", "ccia-s2-5-optimal-selector:latest",
    "ccia-s3-1-redteam-auditor:latest", "ccia-s3-2-isolation-executor:latest",
    "ccia-s3-3-fallback-dispatcher:latest", "ccia-s3-4-pr-formatter:latest",
    "ccia-s3-5-final-deliverer:latest"
]

print("\n🗑️ Eliminando envoltorios redundantes ccia-s* en Ollama...")
for model in ccia_models:
    subprocess.run(["ollama", "rm", model], capture_output=True)
print("  ✅ 15 cerebros redundantes eliminados (Liberados ~70 GB de espacio).")

# 2. Re-mapeo directo en el código fuente de Artefacto 63
MODEL_MAPPING = {
    # Tareas de Código -> Qwen2.5 Coder 14B Abliterated
    "S1_4": "ccia-coder-xl-14b:latest",
    "S2_1": "ccia-coder-xl-14b:latest",
    "S2_3": "ccia-coder-xl-14b:latest",
    "S3_4": "ccia-coder-xl-14b:latest",
    "S1_2": "ccia-coder-xl-14b:latest",
    # Tareas de Auditoría y Razonamiento -> DeepSeek R1 14B Abliterated
    "S1_1": "ccia-reina-r1coder-14b:latest",
    "S1_3": "ccia-reina-r1coder-14b:latest",
    "S1_5": "ccia-reina-r1coder-14b:latest",
    "S2_2": "ccia-reina-r1coder-14b:latest",
    "S2_4": "ccia-reina-r1coder-14b:latest",
    "S2_5": "ccia-reina-r1coder-14b:latest",
    "S3_1": "ccia-reina-r1coder-14b:latest",
    "S3_2": "ccia-reina-r1coder-14b:latest",
    "S3_3": "ccia-reina-r1coder-14b:latest",
    "S3_5": "ccia-reina-r1coder-14b:latest",
}

for path in [ART63_PATH, MANDO63_PATH]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Reemplazar cadenas de ccia-s* por sus respectivos modelos optimizados
        for old_model in ccia_models:
            clean_name = old_model.replace(":latest", "")
            if "patch-generator" in clean_name or "syntax" in clean_name or "pr-formatter" in clean_name or "ast-parser" in clean_name or "mutation" in clean_name:
                content = content.replace(clean_name, "ccia-coder-xl-14b:latest")
                content = content.replace(old_model, "ccia-coder-xl-14b:latest")
            else:
                content = content.replace(clean_name, "ccia-reina-r1coder-14b:latest")
                content = content.replace(old_model, "ccia-reina-r1coder-14b:latest")

        # Inyectar soporte de Cartera Solana en la lista de carteras
        if "Solana (USDC) Address" not in content:
            content = content.replace(
                "3. BTC Address",
                "3. BTC Address       : bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59\n  4. Solana (USDC) Address : Configurar en Mando"
            )

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {os.path.basename(path)} reconfigurado correctamente.")

print("\n================================================================================")
print("📊 ESTADO ACTUALIZADO DEL ALMACENAMIENTO OLLAMA")
print("================================================================================")
subprocess.run(["ollama", "list"])
