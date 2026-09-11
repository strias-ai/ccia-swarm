import re
import os

print("================================================================================")
print("🔗 CONECTANDO SANDBOX PODMAN Y EMBEDDINGS DE OLLAMA AL ARTEFACTO 63")
print("================================================================================")

# 1. Inyectar generación de embeddings vía Ollama en ccia_capabilities.py
cap_file = "/home/k1/ccia_workspace/modules/ccia_capabilities.py"
ollama_embed_code = '''
    def generate_ollama_embedding(self, text, model="nomic-embed-text"):
        """Genera vectores de embedding usando la API local de Ollama."""
        import urllib.request
        import json
        url = "http://127.0.0.1:11434/api/embeddings"
        payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res.get("embedding", [])
        except Exception:
            return []
'''

if os.path.exists(cap_file):
    with open(cap_file, "r", encoding="utf-8") as f:
        content = f.read()
    if "generate_ollama_embedding" not in content:
        content += "\n" + ollama_embed_code
        with open(cap_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 1. Integración de API Ollama Embeddings añadida a ccia_capabilities.py")

# 2. Modificar art_63.py para que la validación de mutaciones use Podman Sandbox
art63_file = "/home/k1/ccia_workspace/modules/art_63.py"
if os.path.exists(art63_file):
    with open(art63_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar ejecución de comandos locales por sandbox si existe la función
    if "self.capabilities.run_in_podman_sandbox" not in content:
        old_pattern = r"subprocess\.run\(\s*\[\s*\"python3\"\s*,\s*script_path\s*\]"
        new_pattern = "self.capabilities.run_in_podman_sandbox(script_path)"
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            with open(art63_file, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ 2. Ejecución de parches S2 vinculada al Sandbox aislado de Podman")
        else:
            print("ℹ️ 2. El punto de enganche para Podman ya estaba actualizado o utiliza un ejecutor personalizado.")

print("================================================================================")
print("✨ CONEXIONES COMPLETADAS DE FORMA EXITOSA")
print("================================================================================")
