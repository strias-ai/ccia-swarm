import glob
import re
import os

print("=== 1. DIAGNÓSTICO DE MÓDULOS Y LLAMADAS EN TEST_ART63_AUTO.PY ===")
test_script = "/home/k1/ccia_workspace/test_art63_auto.py"
if os.path.exists(test_script):
    with open(test_script, "r", encoding="utf-8") as f:
        test_code = f.read()
    print("Imports en test_art63_auto.py:")
    for line in test_code.splitlines():
        if "import" in line or "parse_antispam_decision" in line:
            print("  ", line.strip())

print("\n=== 2. APLICANDO PARCHE SIN REGEX REPLACEMENT (STRING SLICING) ===")

new_parser_code = '''    def parse_antispam_decision(self, raw_out):
        import re
        import json

        raw_str = str(raw_out or "")

        # 1. Búsqueda por Regex directa sobre cadenas puras
        if re.search(r'"valid"\\s*:\\s*false', raw_str, re.IGNORECASE) or re.search(r'"valida"\\s*:\\s*false', raw_str, re.IGNORECASE):
            m_reason = re.search(r'"reason"\\s*:\\s*"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            if not m_reason:
                m_reason = re.search(r'"razon"\\s*:\\s*"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            reason = m_reason.group(1).replace('\\n', ' ').strip() if m_reason else "Spam detectado por Reina Q1."
            return False, reason

        if re.search(r'"valid"\\s*:\\s*true', raw_str, re.IGNORECASE) or re.search(r'"valida"\\s*:\\s*true', raw_str, re.IGNORECASE):
            m_reason = re.search(r'"reason"\\s*:\\s*"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"', raw_str, re.IGNORECASE | re.DOTALL)
            reason = m_reason.group(1).replace('\\n', ' ').strip() if m_reason else "Mensaje válido."
            return True, reason

        # 2. Decodificación de objeto JSON
        try:
            clean = re.sub(r'^\\s*[│|]\\s*', '', raw_str, flags=re.MULTILINE)
            clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'Thinking\\.\\.\\..*?done thinking\\.', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE)

            for match in re.finditer(r'\\{[^{}]*\\}', clean, re.DOTALL):
                try:
                    data = json.loads(match.group(0), strict=False)
                    if isinstance(data, dict) and "valid" in data:
                        return bool(data["valid"]), str(data.get("reason", "Decisión Q1")).replace('\\n', ' ').strip()
                except Exception:
                    continue
        except Exception:
            pass

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"

targets = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for file_path in targets:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            new_content = content[:match.start()] + new_parser_code + content[match.end():]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Parcheado con éxito mediante corte de cadena: {file_path}")
        else:
            print(f"⚠️ No se encontró la función en {file_path}")

