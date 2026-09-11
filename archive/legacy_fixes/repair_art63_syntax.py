import py_compile

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art63_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=" * 80)
print("🔍 INSPECCIONANDO LÍNEAS 120-140 DE ARTEFACTO 63")
print("=" * 80)
for idx in range(max(0, 119), min(len(lines), 140)):
    print(f"Línea {idx+1:3d}: {repr(lines[idx])}")

# Limpiar líneas 'pass' o 'import' mal identadas entre la cabecera def y su cuerpo
cleaned_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Si la línea actual es un 'pass' huérfano insertado antes de un bloque ya identado
    if stripped == "pass" and i + 1 < len(lines):
        next_line = lines[i + 1]
        if next_line.startswith("    ") or next_line.startswith("\t"):
            i += 1
            continue
            
    # Ajustar identación de imports locales inyectados
    if stripped == "import urllib.request, urllib.parse, json":
        line = "    import urllib.request, urllib.parse, json\n"
        
    cleaned_lines.append(line)
    i += 1

with open(art63_path, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print("\n" + "=" * 80)
print("🛠️ VERIFICANDO COMPILACIÓN TRAS LIMPIEZA DE SINTAXIS")
print("=" * 80)

try:
    py_compile.compile(art63_path, doraise=True)
    print("  ✅ COMPILACIÓN EXITOSA: modules/art_63.py listo y verificado.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación detectado:\n{e}")

print("=" * 80)
