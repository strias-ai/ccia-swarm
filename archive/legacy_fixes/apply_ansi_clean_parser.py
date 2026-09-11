import re
import os

new_parser = '''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        if isinstance(raw_out, dict):
            raw_str = str(raw_out.get("response") or raw_out.get("content") or raw_out.get("message") or raw_out)
        elif hasattr(raw_out, "content"):
            raw_str = str(raw_out.content)
        elif hasattr(raw_out, "response"):
            raw_str = str(raw_out.response)
        else:
            raw_str = str(raw_out)

        # 1. Eliminar secuencias de escape ANSI (colores de consola)
        clean = re.sub(r'\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])', '', raw_str)

        # 2. Limpiar prefijos de consola (│, |) e indentación por línea
        clean_lines = [re.sub(r'^\s*[│|]\s*', '', line) for line in clean.splitlines()]
        clean = "\\n".join(clean_lines)

        # 3. Aislar contenido posterior al bloque de razonamiento (thinking)
        for marker in ["...done thinking.", "done thinking.", "</think>"]:
            if marker in clean:
                clean = clean.split(marker)[-1]

        clean = clean.replace("```json", "").replace("```", "").strip()

        # 4. Extraer y evaluar bloques JSON
        for json_str in re.findall(r'\\{[^{}]*\\}', clean, re.DOTALL):
            try:
                data = json.loads(json_str, strict=False)
                if isinstance(data, dict) and ("valid" in data or "valida" in data):
                    v_val = data.get("valid", data.get("valida"))
                    r_val = str(data.get("reason", data.get("razon", ""))).strip()
                    is_valid = bool(v_val) if isinstance(v_val, bool) else str(v_val).lower() in ["true", "1", "si", "sí", "valid"]
                    reason = r_val if r_val else ("Mensaje válido." if is_valid else "Spam detectado por Reina Q1.")
                    return is_valid, reason
            except Exception:
                continue

        # 5. Detección directa por subcadena
        low = clean.lower()
        if '"valid": false' in low or '"valid":false' in low or '"valida": false' in low:
            return False, "Spam detectado por Reina Q1."
        if '"valid": true' in low or '"valid":true' in low or '"valida": true' in low:
            return True, "Mensaje válido verificado por Reina Q1."

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"

targets = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for target in targets:
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            updated = content[:match.start()] + new_parser + content[match.end():]
            with open(target, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"✅ Parser con soporte ANSI actualizado en: {target}")

