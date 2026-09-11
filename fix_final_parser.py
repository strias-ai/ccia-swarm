import re

path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

new_parser_code = r'''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        # 1. Limpieza de prefijos de consola (│) y espacios por línea
        lines = [re.sub(r'^\s*[│|]\s*', '', line) for line in str(raw_out).splitlines()]
        text = "\n".join(lines)

        # 2. Eliminación de bloques de pensamiento (Thinking... / <think>)
        text_clean = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text_clean = re.sub(r'Thinking\.\.\..*?done thinking\.', '', text_clean, flags=re.DOTALL | re.IGNORECASE).strip()

        # 3. Limpieza de bloques Markdown ```json ... ```
        text_clean = re.sub(r'```(?:json)?', '', text_clean, flags=re.IGNORECASE)

        # 4. Decodificación de JSON permitiendo saltos de línea (strict=False)
        json_matches = re.findall(r'\{.*\}', text_clean, re.DOTALL)
        for match in reversed(json_matches):
            try:
                data = json.loads(match, strict=False)
                if isinstance(data, dict):
                    v_val = data.get("valid", data.get("valida"))
                    reason = data.get("reason", data.get("razon", "Detección antispam Q1"))
                    clean_reason = str(reason).replace('\n', ' ').strip()
                    if v_val is False or str(v_val).lower() in ["false", "0", "no", "invalid", "spam"]:
                        return False, clean_reason
                    elif v_val is True or str(v_val).lower() in ["true", "1", "si", "sí", "valid"]:
                        return True, clean_reason
            except Exception:
                continue

        # 5. Búsqueda directa de patrón por texto
        low = text_clean.lower()
        if '"valid": false' in low or '"valid":false' in low:
            m_reason = re.search(r'"reason"\s*:\s*"([^"]+)"', text_clean, re.IGNORECASE | re.DOTALL)
            reason = m_reason.group(1).replace('\n', ' ').strip() if m_reason else "Filtro antispam Q1 detectó valid: false."
            return False, reason

        if '"valid": true' in low or '"valid":true' in low:
            m_reason = re.search(r'"reason"\s*:\s*"([^"]+)"', text_clean, re.IGNORECASE | re.DOTALL)
            reason = m_reason.group(1).replace('\n', ' ').strip() if m_reason else "VÁLIDO"
            return True, reason

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"
match = re.search(pattern, code, flags=re.DOTALL)

if match:
    code = code[:match.start()] + new_parser_code + code[match.end():]
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Módulo art_63.py actualizado exitosamente.")
else:
    print("⚠️ No se encontró la función parse_antispam_decision en art_63.py.")

