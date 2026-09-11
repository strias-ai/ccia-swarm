import glob
import re

py_files = glob.glob("/home/k1/ccia_workspace/**/*.py", recursive=True)

new_parser_code = r'''    def parse_antispam_decision(self, raw_out):
        import re
        import json

        raw_str = str(raw_out or "")

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

        try:
            clean = re.sub(r'^\s*[│|]\s*', '', raw_str, flags=re.MULTILINE)
            clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'Thinking\.\.\..*?done thinking\.', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE)

            for match in re.finditer(r'\{[^{}]*\}', clean, re.DOTALL):
                try:
                    data = json.loads(match.group(0), strict=False)
                    if isinstance(data, dict) and "valid" in data:
                        return bool(data["valid"]), str(data.get("reason", "Decisión Q1")).replace('\n', ' ').strip()
                except Exception:
                    continue
        except Exception:
            pass

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"

for file_path in py_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "def parse_antispam_decision" in content:
            new_content = re.sub(pattern, new_parser_code, content, flags=re.DOTALL)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Sincronizado: {file_path}")
    except Exception as e:
        print(f"Error en {file_path}: {e}")

