import re

path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

new_parser_code = r'''    def parse_antispam_decision(self, raw_out):
        import re
        import json

        raw_str = str(raw_out or "")

        # 1. Detección directa por expresión regular (inmune a formato JSON/Markdown/Consola)
        if re.search(r'"valid"\s*:\s*false', raw_str, re.IGNORECASE) or re.search(r'"valida"\s*:\s*false', raw_str, re.IGNORECASE):
            m_reason = re.search(r'"reason"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            if not m_reason:
                m_reason = re.search(r'"razon"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            
            reason = m_reason.group(1).replace('\n', ' ').strip() if m_reason else "Spam detectado por Reina Q1."
            return False, reason

        if re.search(r'"valid"\s*:\s*true', raw_str, re.IGNORECASE) or re.search(r'"valida"\s*:\s*true', raw_str, re.IGNORECASE):
            m_reason = re.search(r'"reason"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            reason = m_reason.group(1).replace('\n', ' ').strip() if m_reason else "Mensaje válido."
            return True, reason

        # 2. Intento de parseo estructurado estricto
        try:
            clean = re.sub(r'^\s*[│|]\s*', '', raw_str, flags=re.MULTILINE)
            clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'Thinking\.\.\..*?done thinking\.', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE)

            for match in re.finditer(r'\{[^{}]*\}', clean, re.DOTALL):
                try:
                    data = json.loads(match.group(0), strict=False)
                    if isinstance(data, dict) and "valid" in data:
                        v_val = data["valid"]
                        r_val = str(data.get("reason", "Decisión Q1")).replace('\n', ' ').strip()
                        return bool(v_val), r_val
                except Exception:
                    continue
        except Exception:
            pass

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"
match = re.search(pattern, code, flags=re.DOTALL)

if match:
    code = code[:match.start()] + new_parser_code + code[match.end():]
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Módulo art_63.py actualizado con el nuevo parser infalible.")
else:
    print("⚠️ No se encontró la función parse_antispam_decision.")

