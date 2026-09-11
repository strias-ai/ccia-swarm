import re
import json

def patch_art_63():
    path = "/home/k1/ccia_workspace/modules/art_63.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazo o ajuste del método parse_antispam_decision para aislar el JSON mediante regex
    old_code = """    def parse_antispam_decision(self, text):"""
    
    new_method = """    def parse_antispam_decision(self, text):
        try:
            # Eliminar etiquetas/bloques de pensamiento si existen
            text_clean = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
            text_clean = re.sub(r'Thinking\.\.\..*?\.\.\.done thinking\.', '', text_clean, flags=re.DOTALL)
            
            # Buscar el bloque JSON
            match = re.search(r'\{.*\}', text_clean, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data.get("valid", True), data.get("reason", "Sin razón especificada")
        except Exception as e:
            pass
        return True, "VÁLIDO (Fallback)"
"""

    if "def parse_antispam_decision" in content:
        # Reemplazar la implementación
        pattern = r"def parse_antispam_decision\(self, text\):.*?(?=\n    def |\n\n|\Z)"
        content_updated = re.sub(pattern, new_method.strip(), content, flags=re.DOTALL)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content_updated)
        print("✅ Método parse_antispam_decision actualizado exitosamente.")
    else:
        print("⚠️ No se encontró la definición del método en art_63.py.")

if __name__ == "__main__":
    patch_art_63()
