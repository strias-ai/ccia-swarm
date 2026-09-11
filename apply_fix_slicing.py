import re
import os

parser_code = '''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        raw_str = str(raw_out)

        # 1. Limpieza de caracteres de consola
        lines = [re.sub(r'^\\s*[│|]\\s*', '', l) for l in raw_str.splitlines()]
        clean = "\\n".join(lines)

        # 2. Aislamiento del bloque posterior al razonamiento
        if "...done thinking." in clean:
            clean = clean.split("...done thinking.")[-1]
        elif "done thinking." in clean:
            clean = clean.split("done thinking.")[-1]
        elif "</think>" in clean:
            clean = clean.split("</think>")[-1]

        clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE).strip()

        # 3. Extracción de JSON
        json_matches = re.findall(r'\\{[^{}]*\\}', clean, re.DOTALL)
        if not json_matches:
            json_matches = re.findall(r'\\{[^{}]*\\}', raw_str, re.DOTALL)

        for match_str in reversed(json_matches):
            try:
                data = json.loads(match_str, strict=False)
                if isinstance(data, dict) and ("valid" in data or "valida" in data):
                    v_val = data.get("valid", data.get("valida"))
                    reason = data.get("reason", data.get("razon", "Decisión Q1"))
                    clean_reason = str(reason).replace("\\n", " ").strip()

                    if v_val is False or str(v_val).lower() in ["false", "0", "no", "invalid"]:
                        return False, clean_reason
                    elif v_val is True or str(v_val).lower() in ["true", "1", "si", "sí", "valid"]:
                        return True, clean_reason
            except Exception:
                continue

        # 4. Fallback por inspección de texto
        low = clean.lower()
        if '"valid": false' in low or '"valid":false' in low or '"valida": false' in low:
            return False, "Spam detectado por Reina Q1 (Fallback Regex)."
        if '"valid": true' in low or '"valid":true' in low or '"valida": true' in low:
            return True, "Mensaje válido verificado por Reina Q1 (Fallback Regex)."

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
            updated = content[:match.start()] + parser_code + content[match.end():]
            with open(target, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"✅ Actualizado con éxito: {target}")

