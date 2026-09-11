import re

path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

new_parser_code = r'''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        # 1. Limpieza de prefijos de consola (│) y espacios
        lines = [re.sub(r'^\s*[│|]\s*', '', line) for line in str(raw_out).splitlines()]
        clean_text = "\n".join(lines)

        # 2. Búsqueda directa por expresión regular sobre clave/valor booleanos
        m_valid = re.search(r'"valid"\s*:\s*(false|true)', clean_text, re.IGNORECASE)
        m_reason = re.search(r'"reason"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', clean_text, re.IGNORECASE)
        
        reason = m_reason.group(1) if m_reason else "Razón detectada por el modelo Q1"

        if m_valid:
            is_valid = (m_valid.group(1).lower() == "true")
            return is_valid, reason

        # 3. Extracción de objeto JSON alternativo
        for match in re.finditer(r'\{[^{}]*\}', clean_text, re.DOTALL):
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict) and "valid" in data:
                    return bool(data["valid"]), str(data.get("reason", reason))
            except Exception:
                continue

        # 4. Comprobación literal
        low = clean_text.lower()
        if '"valid": false' in low or '"valid":false' in low:
            return False, reason

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"
match = re.search(pattern, code, flags=re.DOTALL)

if match:
    code = code[:match.start()] + new_parser_code + code[match.end():]
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Módulo art_63.py parcheado exitosamente.")
else:
    print("⚠️ No se encontró la función parse_antispam_decision.")

