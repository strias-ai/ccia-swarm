import re

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(mando_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

# Detectar la sangría exacta del condicional en el archivo
base_indent = None
for line in lines:
    match = re.match(r'^(\s*)(if|elif)\s+opt\s*==\s*"1"', line)
    if match:
        base_indent = match.group(1)
        break

if not base_indent:
    for line in lines:
        match = re.match(r'^(\s*)(if|elif)\s+opt\s*==', line)
        if match:
            base_indent = match.group(1)
            break

if not base_indent:
    base_indent = "            "

body_indent = base_indent + "    "

new_opt2 = f'''{base_indent}elif opt == "2":
{body_indent}print("\\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA:")
{body_indent}print("Modelos instalados detectados:")
{body_indent}models = orch.available_models
{body_indent}for idx, m in enumerate(models, 1):
{body_indent}    print(f"  {{idx}}. {{m}}")
{body_indent}
{body_indent}print("\\nSeleccione Cerebro a reconfigurar (ejemplo: 1.1, 2.3, Q1, o 'TODOS'):")
{body_indent}target = input("Código de Cerebro > ").strip()
{body_indent}if target:
{body_indent}    print(f"\\nIndique el modelo deseado escribiendo su NÚMERO (1-{{len(models)}}) o el NOMBRE EXACTO:")
{body_indent}    val = input("Modelo (Número o Nombre) > ").strip()
{body_indent}    selected_model = None
{body_indent}    if val.isdigit() and 1 <= int(val) <= len(models):
{body_indent}        selected_model = models[int(val) - 1]
{body_indent}    elif val in models:
{body_indent}        selected_model = val
{body_indent}    else:
{body_indent}        print("⚠️ Selección no válida.")
{body_indent}
{body_indent}    if selected_model:
{body_indent}        if target.upper() == "TODOS":
{body_indent}            for b in orch.brains: b["model"] = selected_model
{body_indent}            for q in orch.queen_brains: q["model"] = selected_model
{body_indent}        else:
{body_indent}            for b in orch.brains:
{body_indent}                if b["code"].upper() == target.upper(): b["model"] = selected_model
{body_indent}            for q in orch.queen_brains:
{body_indent}                if q["code"].upper() == target.upper(): q["model"] = selected_model
{body_indent}        
{body_indent}        orch.save_swarm_config()
{body_indent}        print(f"\\n✅ Cerebro(s) [{{target.upper()}}] reconfigurado(s) exitosamente a: {{selected_model}}")
{body_indent}input("\\n[Presione ENTER para continuar...]")'''

pattern = r'^\s*elif opt == "2":.*?(?=^\s*elif opt == "3":)'
if re.search(pattern, content, re.DOTALL | re.MULTILINE):
    content = re.sub(pattern, new_opt2 + "\n\n", content, flags=re.DOTALL | re.MULTILINE)
    with open(mando_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Indentación corregida exitosamente (Sangría alineada a {len(base_indent)} espacios).")
else:
    print("⚠️ No se pudo localizar el bloque objetivo.")
