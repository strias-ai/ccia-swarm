import re
import os

clean_func = '''    def parse_antispam_decision(self, raw_out):
        import json

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

        lines = []
        for line in raw_str.splitlines():
            line_str = line.strip()
            if line_str.startswith("│") or line_str.startswith("|"):
                line_str = line_str[1:].strip()
            lines.append(line_str)
        clean = "\\n".join(lines)

        for marker in ["...done thinking.", "done thinking.", "</think>"]:
            if marker in clean:
                clean = clean.split(marker)[-1]

        clean = clean.replace("```json", "").replace("```", "").strip()

        start_idx = clean.rfind("{")
        end_idx = clean.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_candidate = clean[start_idx : end_idx + 1]
            try:
                data = json.loads(json_candidate, strict=False)
                if isinstance(data, dict):
                    v_val = data.get("valid", data.get("valida"))
                    r_val = str(data.get("reason", data.get("razon", ""))).strip()
                    if v_val is not None:
                        is_valid = bool(v_val) if isinstance(v_val, bool) else str(v_val).lower() in ["true", "1", "si", "sí", "valid"]
                        reason = r_val if r_val else ("Mensaje válido." if is_valid else "Spam detectado por Reina Q1.")
                        return is_valid, reason
            except Exception:
                pass

        start_idx = raw_str.rfind("{")
        end_idx = raw_str.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_candidate = raw_str[start_idx : end_idx + 1]
            try:
                data = json.loads(json_candidate, strict=False)
                if isinstance(data, dict):
                    v_val = data.get("valid", data.get("valida"))
                    r_val = str(data.get("reason", data.get("razon", ""))).strip()
                    if v_val is not None:
                        is_valid = bool(v_val) if isinstance(v_val, bool) else str(v_val).lower() in ["true", "1", "si", "sí", "valid"]
                        reason = r_val if r_val else ("Mensaje válido." if is_valid else "Spam detectado por Reina Q1.")
                        return is_valid, reason
            except Exception:
                pass

        clean_low = clean.lower()
        if '"valid": false' in clean_low or '"valid":false' in clean_low or '"valida": false' in clean_low:
            return False, "Spam detectado por Reina Q1 (Fallback)."
        if '"valid": true' in clean_low or '"valid":true' in clean_low or '"valida": true' in clean_low:
            return True, "Mensaje válido (Fallback)."

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
            updated = content[:match.start()] + clean_func + content[match.end():]
            with open(target, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"✅ Método sustituido exitosamente en: {target}")

