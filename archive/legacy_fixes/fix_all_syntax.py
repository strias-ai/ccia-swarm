import py_compile
import re

def sanitize_file(filepath):
    print(f"🔍 Sanitizando sintaxis y comillas en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Reemplazo seguro de f-strings que contienen comillas dobles o llaves mal formateadas
    new_lines = []
    for line in content.splitlines():
        if 'eval_plan =' in line and '{"valid": true}' in line:
            line = '        json_spec = \'{"valid": true, "reason": "..."}\'\n        eval_plan = self.call_ollama_direct(q1_model, "Reina Q2 Auditora", f"Evaluar plan:\\n{plan[:300]}\\n¿Es viable? Responder JSON: " + json_spec)'
        elif 'check_prompt =' in line and '{"valid": true' in line:
            line = '        json_spec = \'{"valid": true, "reason": "..."}\'\n        check_prompt = f"Evaluar bounty {repo}#{issue_id}. Responder estricto JSON: " + json_spec'
        new_lines.append(line)

    content = "\n".join(new_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} SANITIZADO Y COMPILADO CON ÉXITO.")
        return True
    except Exception as e:
        print(f"  ❌ Error de compilación en {filepath}:\n{e}")
        return False

sanitize_file("/home/k1/ccia_workspace/modules/art_63.py")
sanitize_file("/home/k1/ccia_workspace/ccia_mando_63.py")
