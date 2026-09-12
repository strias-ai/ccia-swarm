import re
import os

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

if not os.path.exists(art63_path):
    print("❌ Archivo modules/art_63.py no encontrado.")
    exit(1)

with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

print("=" * 80)
print("🛠️ APLICANDO CORRECCIÓN DE DEUDA TÉCNICA EN ARTEFACTO 63")
print("=" * 80)

# A. Inyectar clase StreamThinkFilter para ocultar trazas <think> en tiempo real
stream_filter_class = '''
class StreamThinkFilter:
    """Buffer que intercepta y remueve etiquetas <think>...</think> durante el streaming token a token."""
    def __init__(self):
        self.buffer = ""
        self.in_think = False

    def process(self, chunk: str) -> str:
        self.buffer += chunk
        output = ""
        while True:
            if not self.in_think:
                if "<think>" in self.buffer:
                    before, after = self.buffer.split("<think>", 1)
                    output += before
                    self.buffer = after
                    self.in_think = True
                else:
                    idx = self.buffer.rfind("<")
                    if idx != -1 and "<think>".startswith(self.buffer[idx:]):
                        output += self.buffer[:idx]
                        self.buffer = self.buffer[idx:]
                    else:
                        output += self.buffer
                        self.buffer = ""
                    break
            else:
                if "</think>" in self.buffer:
                    _, after = self.buffer.split("</think>", 1)
                    self.buffer = after
                    self.in_think = False
                else:
                    self.buffer = ""
                    break
        return output
'''

if "class StreamThinkFilter" not in code:
    code = stream_filter_class + "\n" + code
    print("  ✅ [1/4] Filtro de Streaming Token a Token (StreamThinkFilter) inyectado.")

# B. Método de llamada a Ollama con Timeout y Fallback
fallback_logic = '''
    def call_ollama_safe(self, model: str, prompt: str, fallback_model: str = "ccia-coder-xl-14b:latest", timeout: int = 120):
        """Ejecuta inferencia con fallback automático en caso de timeout o falta de VRAM."""
        try:
            import requests
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout
            )
            if res.status_code == 200:
                text = res.json().get("response", "")
                return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        except Exception as e:
            print(f"\\n⚠️ Timeout/Error en modelo [{model}]: {e}. Reintentando con fallback [{fallback_model}]...")
        
        # Fallback
        try:
            import requests
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": fallback_model, "prompt": prompt, "stream": False},
                timeout=60
            )
            if res.status_code == 200:
                text = res.json().get("response", "")
                return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        except Exception as f_err:
            return f"❌ Error de inferencia en modelos {model} y {fallback_model}: {f_err}"
'''

if "def call_ollama_safe" not in code:
    # Insertar dentro de la clase principal
    class_match = re.search(r'class\s+\w+.*?:', code)
    if class_match:
        pos = class_match.end()
        code = code[:pos] + "\n" + fallback_logic + code[pos:]
        print("  ✅ [2/4] Lógica de Fallback de VRAM / Timeout inyectada.")

# C. Verificación de GITHUB_TOKEN
token_check = '''
    def get_github_token(self):
        """Recupera el Token de GitHub desde las variables de entorno."""
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT")
        if not token:
            print("⚠️ ADVERTENCIA: GITHUB_TOKEN no configurado en el entorno. Modo Solo-Lectura activo.")
        return token
'''

if "def get_github_token" not in code:
    class_match = re.search(r'class\s+\w+.*?:', code)
    if class_match:
        pos = class_match.end()
        code = code[:pos] + "\n" + token_check + code[pos:]
        print("  ✅ [3/4] Gestor de Credenciales de GitHub inyectado.")

# Guardar cambios
with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ [4/4] Archivo modules/art_63.py actualizado y guardado.")

print("=" * 80)
print("🚀 DEUDA TÉCNICA REPARADA EXITOSAMENTE")
print("=" * 80)
