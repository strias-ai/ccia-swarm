import os
import py_compile

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("=" * 80)
print("🔍 VERIFICANDO INTEGRIDAD DEL CENTRO DE MANDO (13 OPCIONES)")
print("=" * 80)

if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificar presencia de las 13 opciones principales
    options_check = [
        "[1]", "[2]", "[3]", "[4]", "[5]", "[6]", 
        "[7]", "[8]", "[9]", "[10]", "[11]", "[12]", "[13]"
    ]
    present = [opt for opt in options_check if opt in content]
    
    print(f"  ✅ Opciones de mando detectadas en código: {len(present)}/13")
    
    try:
        py_compile.compile(mando_path, doraise=True)
        print("  ✅ Compilación limpia sin errores sintácticos.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error de compilación:\n{e}")
else:
    print("  ❌ Archivo ccia_mando_63.py no encontrado.")

print("=" * 80)
