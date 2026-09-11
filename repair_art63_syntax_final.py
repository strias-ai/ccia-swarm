import re
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

CLEAN_WALLET_FUNC = '''
def mostrar_carteras():
    print("💳 CONFIGURACIÓN DE CARTERAS DE RECEPCIÓN (CCiA HUB)")
    print("  1. Lightning Address            : vellichorlate475846@getalby.com")
    print("  2. EVM (ETH/Base/Arb/OP/Polygon): 0x6040f4D8BA36214222d34E176634670407a9bC56")
    print("  3. BTC Address (Native SegWit)  : bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59")
    print("  4. Solana (USDC/SOL - Superteam): Configurar en Mando")
    print("  5. TON Network (Telegram Bots)  : Configurar en Mando")
    print("  6. Sui Network (Move Bounties)  : Configurar en Mando")
    print("  7. NEAR Protocol (AI Agent Hub) : Configurar en Mando")
'''

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: REPARACIÓN SINTÁCTICA DEFINITIVA DE ARTEFACTO 63")
print("================================================================================")

for file_path in FILES:
    print(f"\n🔍 Reparando archivo: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    clean_lines = []
    for line in lines:
        # Filtrar la línea corrupta que provocaba el SyntaxError
        if 'print("\\ndef mostrar_carteras():' in line or 'print(f"  3. BTC Address' in line or 'def mostrar_carteras():' in line:
            continue
        clean_lines.append(line)

    new_content = "".join(clean_lines) + "\n" + CLEAN_WALLET_FUNC

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    try:
        py_compile.compile(file_path, doraise=True)
        print(f"  ✅ {file_path} SINTAXIS CERTIFICADA Y COMPILADA SIN ERRORES.")
    except Exception as e:
        print(f"  ❌ Error en {file_path}: {e}")

print("\n================================================================================")
print("✅ PROCESO COMPLETADO. EJECUTA 'ccia1' -> OPCIÓN 4 PARA LANZAR MANDO.")
print("================================================================================")
