import subprocess

# Modelos < 7B identificados para eliminación
SMALL_MODELS = [
    "qwen2.5-coder:3b",
    "deepseek-r1:1.5b",
    "llama3.2:1b",
    "gemma2:2b",
    "qwen2.5:3b",
    "stable-code:3b",
    "falcon3:3b",
    "qwen2.5:1.5b",
    "llama3.2:3b",
    "qwen2-math:1.5b",
    "phi3:mini"
]

print("================================================================================")
print("🧹 CCiA ENGINE: LIMPIEZA DE CEREBROS Y MODELOS OLLAMA < 7B")
print("================================================================================")

for model in SMALL_MODELS:
    print(f"🗑️ Eliminando modelo sub-7B: {model} ...")
    res = subprocess.run(["ollama", "rm", model], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"  ✅ {model} eliminado correctamente.")
    else:
        print(f"  ⚠️ {model}: {res.stderr.strip() or 'No encontrado o ya eliminado.'}")

print("\n================================================================================")
print("📊 ESTADO DEL ALMACENAMIENTO RESTANTE EN OLLAMA")
print("================================================================================")
subprocess.run(["ollama", "list"])
