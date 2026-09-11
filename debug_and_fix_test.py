import re
import os

print("=== 1. BUSCANDO OCURRENCIAS DE 'parse_antispam_decision' Y 'Fallback' EN TODO EL WORKSPACE ===")
for root, dirs, files in os.walk("/home/k1/ccia_workspace"):
    for file in files:
        if file.endswith(".py"):
            fpath = os.path.join(root, file)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "parse_antispam_decision" in content:
                    print(f"📄 Encontrado 'parse_antispam_decision' en: {fpath}")
                if "VÁLIDO (Fallback)" in content:
                    print(f"📄 Encontrado 'VÁLIDO (Fallback)' en: {fpath}")

print("\n=== 2. CONTENIDO DE TEST_ART63_AUTO.PY (SECCIÓN 3 DE SPAM) ===")
with open("/home/k1/ccia_workspace/test_art63_auto.py", "r", encoding="utf-8") as f:
    test_lines = f.readlines()

for idx, line in enumerate(test_lines):
    if "RECHAZO DE SPAM" in line or "parse_antispam_decision" in line or "Decisión Parseada" in line:
        start = max(0, idx - 5)
        end = min(len(test_lines), idx + 15)
        print(f"--- Líneas {start} a {end} en test_art63_auto.py ---")
        print("".join(test_lines[start:end]))
        break

