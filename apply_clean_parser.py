import re

parser_code = '''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        raw_str = str(raw_out)

        # 1. Limpieza de líneas con prefijos de consola ('│', '|')
        clean_lines = [re.sub(r'^\s*[│|]\s*', '', line) for line in raw_str.splitlines()]
        clean = "\n".join(clean_lines)

        # 2. Eliminación de razonamientos de pensador (Thinking... / <think>)
        clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'Thinking\.\.\..*?done thinking\.', '', clean, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE).strip()

        # 3. Extracción y parseo de objeto JSON
        json_match = re.search(r'\{.*\}', clean, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0), strict=False)
                if isinstance(data, dict):
                    v_val = data.get("valid", data.get("valida"))
                    reason = data.get("reason", data.get("razon", "Decisión Q1"))
                    clean_reason = str(reason).replace('\n', ' ').strip()
                    
                    if v_val is False or str(v_val).lower() in ["false", "0", "no", "invalid"]:
                        return False, clean_reason
                    elif v_val is True or str(v_val).lower() in ["true", "1", "si", "sí", "valid"]:
                        return True, clean_reason
            except Exception:
                pass

        # 4. Fallback por detección directa en texto limpia
        low = clean.lower()
        if '"valid": false' in low or '"valid":false' in low:
            return False, "Spam detectado por Reina Q1 (Regex direct)."
        if '"valid": true' in low or '"valid":true' in low:
            return True, "Mensaje válido verificado por Reina Q1 (Regex direct)."

        return True, "VÁLIDO (Fallback)"
'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"

for path in ["/home/k1/ccia_workspace/modules/art_63.py", "/home/k1/ccia_workspace/ccia_mando_63.py"]:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    
    match = re.search(pattern, code, flags=re.DOTALL)
    if match:
        updated = code[:match.start()] + parser_code + code[match.end():]
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"✅ Parser actualizado correctamente en {path}")

