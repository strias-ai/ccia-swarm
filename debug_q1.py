import re
import sys

print("--- 1. OCURRENCIAS DE parse_antispam_decision EN art_63.py ---")
with open("/home/k1/ccia_workspace/modules/art_63.py", "r", encoding="utf-8") as f:
    art_content = f.read()

matches = [m.start() for m in re.finditer(r"def parse_antispam_decision", art_content)]
print(f"Definiciones encontradas: {len(matches)}")

for idx, match_pos in enumerate(matches, 1):
    print(f"\n--- [DEFINICIÓN {idx}] ---")
    print(art_content[match_pos:match_pos+600])

print("\n--- 2. CÓMO SE INVOCAN LAS LLAMADAS EN art_63.py ---")
call_matches = [m.start() for m in re.finditer(r"parse_antispam_decision\(", art_content)]
for cp in call_matches:
    line_start = art_content.rfind('\n', 0, cp)
    line_end = art_content.find('\n', cp)
    print("Llamada:", art_content[line_start:line_end].strip())

print("\n--- 3. PRUEBA DIRECTA DE EJECUCIÓN CON LA SALIDA REAL ---")
sample_text = """Thinking...
  │ {"valid": false, "reason": "El mensaje sugiere una estrategia de spam al crear un número arbitrario y específico de issues..."}
  │   📡 --- FIN STREAM DE RAZONAMIENTO ---"""

sys.path.insert(0, "/home/k1/ccia_workspace/modules")
try:
    import art_63
    for name in dir(art_63):
        obj = getattr(art_63, name)
        if isinstance(obj, type) and hasattr(obj, "parse_antispam_decision"):
            try:
                inst = obj()
                res = inst.parse_antispam_decision(sample_text)
                print(f"Resultado en clase {name}: {res}")
            except Exception as e:
                print(f"Error evaluando {name}: {e}")
except Exception as e:
    print(f"Error al importar art_63: {e}")

