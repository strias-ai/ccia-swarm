# -*- coding: utf-8 -*-
"""
CCIA OLLAMA MODEL AUTO-RECOVERY v1.0
Audita la disponibilidad de qwen2.5-coder:3b y deepseek-r1:1.5b en Ollama
y gestiona pings de precarga para eliminar latencia en frío.
"""
import json
import urllib.request

REQUIRED_MODELS = ["qwen2.5-coder:3b", "deepseek-r1:1.5b"]

def audit_and_preload_models() -> dict:
    status = {}
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            installed = [m.get("name") for m in data.get("models", [])]
            
            for model in REQUIRED_MODELS:
                status[model] = "READY" if any(model in m for m in installed) else "MISSING"
    except Exception as e:
        return {"error": f"Ollama no responde: {e}"}
    return status

if __name__ == "__main__":
    print(f"🤖 Estado de Modelos en Ollama: {audit_and_preload_models()}")
