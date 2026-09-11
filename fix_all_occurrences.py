import os
import re
import glob

# 1. Localizar todos los archivos Python en el workspace que contengan el parser
py_files = glob.glob("/home/k1/ccia_workspace/**/*.py", recursive=True)

target_files = []
for fpath in py_files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            if "parse_antispam_decision" in content or "VÁLIDO (Fallback)" in content:
                target_files.append(fpath)
    except Exception:
        pass

print(f"Archivos identificados para actualización: {target_files}")

# 2. Implementación robusta que aísla la salida posterior al razonamiento
parser_code = '''    def parse_antispam_decision(self, raw_out):
        import json
        import re

        if not raw_out:
            return True, "VÁLIDO (Sin respuesta)"

        raw_str = str(raw_out)

        # Limpiar prefijos de consola
        clean_lines = [re.sub(r'^\s*[│|]\s*', '', line) for line in raw_str.splitlines()]
        clean = "\\n".join(clean_lines)

        # Tomar la salida posterior al bloque de razonamiento
        if "...done thinking." in clean:
            clean = clean.split("...done thinking.")[-1]
        elif "done thinking." in clean:
            clean = clean.split("done thinking.")[-1]
        elif "</think>" in clean:
            clean = clean.split("</think>")[-1]

        clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE).strip()

        # Extraer el último objeto JSON en la salida final
        json_matches = re.findall(r'\{[^{}]*\}', clean, re.DOTALL)
        if not json_matches:
            json_matches = re.findall(r'\{[^{}]*\}', raw_str, re.DOTALL)

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

        low = clean.lower()
        if '"valid": false' in low or '"valid":false' in low or '"valida": false' in low:
            return False, "Spam detectado por Reina Q1 (Fallback Regex)."
        if '"valid": true' in low or '"valid":true' in low or '"valida": true' in low:
            return True, "Mensaje válido verificado por Reina Q1 (Fallback Regex)."

        return True, "VÁLIDO (Fallback)"'''

pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"

for fpath in target_files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    if re.search(pattern, content, flags=re.DOTALL):
        updated = re.sub(pattern, parser_code, content, flags=re.DOTALL)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"✅ Parser actualizado en: {fpath}")

