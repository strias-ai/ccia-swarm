import re

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    func_lines = [
        "    def parse_antispam_decision(self, raw_out):",
        "        import json",
        "        import re",
        "",
        "        if not raw_out:",
        '            return True, "VÁLIDO (Sin respuesta)"',
        "",
        "        raw_str = str(raw_out)",
        "",
        "        clean_lines = []",
        "        for line in raw_str.splitlines():",
        "            clean_lines.append(re.sub(r'^\s*[│|]\s*', '', line))",
        '        clean = "\\n".join(clean_lines)',
        "",
        "        clean = re.sub(r'<think>.*?</think>', '', clean, flags=re.DOTALL | re.IGNORECASE)",
        "        clean = re.sub(r'Thinking\\.\\.\\..*?done thinking\\.', '', clean, flags=re.DOTALL | re.IGNORECASE)",
        "        clean = re.sub(r'```(?:json)?', '', clean, flags=re.IGNORECASE).strip()",
        "",
        "        json_match = re.search(r'\\{.*\\}', clean, re.DOTALL)",
        "        if json_match:",
        "            try:",
        "                data = json.loads(json_match.group(0), strict=False)",
        "                if isinstance(data, dict):",
        '                    v_val = data.get("valid", data.get("valida"))',
        '                    reason = data.get("reason", data.get("razon", "Decisión Q1"))',
        '                    clean_reason = str(reason).replace("\\n", " ").strip()',
        "                    ",
        '                    if v_val is False or str(v_val).lower() in ["false", "0", "no", "invalid"]:',
        "                        return False, clean_reason",
        '                    elif v_val is True or str(v_val).lower() in ["true", "1", "si", "sí", "valid"]:',
        "                        return True, clean_reason",
        "            except Exception:",
        "                pass",
        "",
        "        low = clean.lower()",
        '        if \'"valid": false\' in low or \'"valid":false\' in low or \'"valida": false\' in low:',
        '            return False, "Spam detectado por Reina Q1 (Regex direct)."',
        '        if \'"valid": true\' in low or \'"valid":true\' in low or \'"valida": true\' in low:',
        '            return True, "Mensaje válido verificado por Reina Q1 (Regex direct)."',
        "",
        '        return True, "VÁLIDO (Fallback)"'
    ]
    
    new_func = "\n".join(func_lines)

    pattern = r"    def parse_antispam_decision\(self, [^\)]+\):.*?(?=\n    def |\Z)"
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        updated = content[:match.start()] + new_func + content[match.end():]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"✅ Archivo reparado con éxito: {path}")

for target in ["/home/k1/ccia_workspace/modules/art_63.py", "/home/k1/ccia_workspace/ccia_mando_63.py"]:
    fix_file(target)

