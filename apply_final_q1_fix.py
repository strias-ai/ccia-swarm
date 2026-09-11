import re
import os

new_parser_code = '''    def parse_antispam_decision(self, raw_out):
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

        clean_lines = [re.sub(r'^\\s*[│|]\\s*', '', line) for line in raw_str.splitlines()]
        clean = "\\n".join(clean_lines)

        if "...done thinking." in clean:
            clean = clean.split("...done thinking.")[-1]
        elif "done thinking." in clean:
            clean = clean.split("done thinking.")[-1]
        elif "</think>" in clean:
            clean = clean.split("</think>")[-1]

        clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE).strip()

        match_valid = re.search(r'["\\']?valid(?:a)?["\\']?\\s*:\\s*(true|false)', clean, re.IGNORECASE)
        if not match_valid:
            match_valid = re.search(r'["\\']?valid(?:a)?["\\']?\\s*:\\s*(true|false)', raw_str, re.IGNORECASE)

        m_reason = re.search(r'["\\']?reason["\\']?\\s*:\\s*["\\']([^"\\\\'\\n]*(?:\\\\.[^"\\\\'\\n]*)*)["\\']', clean, re.IGNORECASE | re.DOTALL)
        if not m_reason:
            m_reason = re.search(r'["\\']?reason["\\']?\\s*:\\s*["\\']([^"\\\\'\\n]*(?:\\\\.[^"\\\\'\\n]*)*)["\\']', raw_str, re.IGNORECASE | re.DOTALL)

        reason_text = m_reason.group(1).replace('\\n', ' ').strip() if m_reason else ""

        if match_valid:
            is_valid_bool = match_valid.group(1).lower() == "true"
            final_reason = reason_text if reason_text else ("Mensaje válido." if is_valid_bool else "Spam detectado por Reina Q1.")
            return is_valid_bool, final_reason

        for m in reversed(re.findall(r'\\{[^{}]*\\}', clean, re.DOTALL)):
            try:
                data = json.loads(m, strict=False)
                if isinstance(data, dict) and ("valid" in data or "valida" in data):
                    v_val = data.get("valid", data.get("valida"))
                    r_val = str(data.get("reason", data.get("razon", ""))).replace('\\n', ' ').strip()
                    is_valid_bool = bool(v_val) if isinstance(v_val, bool) else str(v_val).lower() in ["true", "1", "si", "sí", "valid"]
                    return is_valid_bool, r_val if r_val else ("Mensaje válido." if is_valid_bool else "Spam detectado por Reina Q1.")
            except Exception:
                continue

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
            updated = content[:match.start()] + new_parser_code + content[match.end():]
            with open(target, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"✅ Parser actualizado en {target}")

