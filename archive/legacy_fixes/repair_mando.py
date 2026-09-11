import sys
import py_compile

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

with open(mando_path, "r", encoding="utf-8") as f:
    content = f.read()

idx_opt2 = content.find('opt == "2"')
idx_opt3 = content.find('opt == "3"')

if idx_opt2 == -1 or idx_opt3 == -1:
    print("❌ No se encontraron los índices de la Opción 2 u Opción 3 en el archivo.")
    sys.exit(1)

line_start_2 = content.rfind('\n', 0, idx_opt2) + 1
line_start_3 = content.rfind('\n', 0, idx_opt3) + 1

lines_opt2 = [
    '        elif opt == "2":',
    '            print("\\n🧠 RECONFIGURACIÓN DE MODELOS OLLAMA:")',
    '            print("Modelos instalados detectados:")',
    '            models = orch.available_models',
    '            for idx, m in enumerate(models, 1):',
    '                print(f"  {idx}. {m}")',
    '            print("\\nSeleccione Cerebro a reconfigurar (ejemplo: 1.1, 2.3, Q1, o \'TODOS\'):")',
    '            target = input("Código de Cerebro > ").strip()',
    '            if target:',
    '                print(f"\\nIndique el modelo deseado escribiendo su NÚMERO (1-{len(models)}) o el NOMBRE EXACTO:")',
    '                val = input("Modelo (Número o Nombre) > ").strip()',
    '                selected_model = None',
    '                if val.isdigit() and 1 <= int(val) <= len(models):',
    '                    selected_model = models[int(val) - 1]',
    '                elif val in models:',
    '                    selected_model = val',
    '                else:',
    '                    print("⚠️ Selección no válida.")',
    '                if selected_model:',
    '                    if target.upper() == "TODOS":',
    '                        for b in orch.brains: b["model"] = selected_model',
    '                        for q in orch.queen_brains: q["model"] = selected_model',
    '                    else:',
    '                        for b in orch.brains:',
    '                            if b["code"].upper() == target.upper(): b["model"] = selected_model',
    '                        for q in orch.queen_brains:',
    '                            if q["code"].upper() == target.upper(): q["model"] = selected_model',
    '                    orch.save_swarm_config()',
    '                    print(f"\\n✅ Cerebro(s) [{target.upper()}] reconfigurado(s) exitosamente a: {selected_model}")',
    '            input("\\n[Presione ENTER para continuar...]")',
]

replacement_block = "\n".join(lines_opt2) + "\n\n"
new_content = content[:line_start_2] + replacement_block + content[line_start_3:]

with open(mando_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ Estructura del menú reconstruida correctamente.")

try:
    py_compile.compile(mando_path, doraise=True)
    print("🎉 ¡Compilación de Python EXITOSA! Sin errores de sintaxis.")
except Exception as e:
    print(f"❌ Error de compilación: {e}")
