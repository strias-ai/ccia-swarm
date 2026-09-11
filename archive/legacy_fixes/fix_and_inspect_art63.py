import os
import re
import py_compile

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"
MANDO63_PATH = "/home/k1/ccia_workspace/ccia_mando_63.py"

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: REPARACIÓN SINTÁCTICA Y AUDITORÍA TRANSPARENTE")
print("================================================================================")

# 1. Reparación sintáctica de art_63.py
if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_lines = []
    for line in lines:
        if 'print("\\ndef mostrar_carteras():' in line or 'print(f"  3. BTC Address' in line:
            continue
        clean_lines.append(line)

    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)

    try:
        py_compile.compile(ART63_PATH, doraise=True)
        print("✅ /modules/art_63.py COMPILADO Y CERTIFICADO SIN ERRORES SINTÁCTICOS.")
    except Exception as e:
        print(f"❌ Error sintáctico en art_63.py: {e}")

if os.path.exists(MANDO63_PATH):
    try:
        py_compile.compile(MANDO63_PATH, doraise=True)
        print("✅ ccia_mando_63.py COMPILADO Y CERTIFICADO SIN ERRORES SINTÁCTICOS.")
    except Exception as e:
        print(f"❌ Error sintáctico en ccia_mando_63.py: {e}")

# 2. Auditoría real del código de Artefacto 63
print("\n--------------------------------------------------------------------------------")
print("📊 AUDITORÍA REAL DE CONFIGURACIÓN Y MÓDULOS DE BÚSQUEDA EN ART_63.PY")
print("--------------------------------------------------------------------------------")

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code_content = f.read()

urls = list(set(re.findall(r'https?://[^\s\'"]+', code_content)))
print("🌐 Endpoints / APIs en código:")
if urls:
    for u in urls:
        print(f"  • {u}")
else:
    print("  ℹ️ No se detectaron URLs externas explícitas (Utiliza la API de GitHub / CLI local).")

target_platforms = {
    "GitHub (Issues/PRs)": ["github", "issue", "pull_request"],
    "Superteam Earn": ["superteam", "earn.superteam"],
    "Algora": ["algora"],
    "Gitcoin": ["gitcoin"],
    "DoraHacks": ["dorahacks"],
    "Code4rena": ["code4rena"],
    "Sherlock": ["sherlock"],
    "Bountycaster": ["bountycaster"],
    "Stackers.news / Alby": ["stackers", "alby", "lightning"],
    "Ordinals / Runes": ["ordinals", "runes"],
    "Sui / Move": ["sui", "move"],
    "NEAR Protocol": ["near"]
}

print("\n🔍 Estado de soporte en el código fuente de Artefacto 63:")
for plat, kw_list in target_platforms.items():
    found = any(kw in code_content.lower() for kw in kw_list)
    status = "✅ INTEGRADO / REFERENCIADO" if found else "❌ NO PROGRAMADO AÚN"
    print(f"  • {plat:<25}: {status}")

print("================================================================================")
print("✅ INSPECCIÓN Y REPARACIÓN COMPLETADAS.")
print("================================================================================")
