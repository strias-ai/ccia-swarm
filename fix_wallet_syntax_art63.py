import re
import py_compile

FILES = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

WALLET_MENU_CODE = '''def mostrar_carteras():
    print("💳 CONFIGURACIÓN DE CARTERAS DE RECEPCIÓN (CCiA HUB)")
    print("  1. Lightning Address            : vellichorlate475846@getalby.com")
    print("  2. EVM (ETH/Base/Arb/OP/Polygon): 0x6040f4D8BA36214222d34E176634670407a9bC56")
    print("  3. BTC Address (Native SegWit)  : bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59")
    print("  4. Solana (USDC/SOL - Superteam): Configurar dirección SOL")
    print("  5. TON Network (Telegram Bots)  : Configurar dirección TON")
    print("  6. Sui Network (Move Bounties)  : Configurar dirección SUI")
    print("  7. NEAR Protocol (AI Agent Hub) : Configurar dirección NEAR")
'''

print("================================================================================")
print("🛠️ CCiA REPARADOR SINTÁCTICO DE CARTERAS Y MANDO 63")
print("================================================================================")

for file_path in FILES:
    print(f"🔍 Procesando: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Arreglar la línea rota de f-string en el código
    pattern = r'print\(f"\s*3\. BTC Address\s*: bc1q[^\n]*'
    if re.search(pattern, code):
        code = re.sub(
            r'print\(f"\s*3\. BTC Address.*?\n',
            'print("  3. BTC Address       : bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59")\n',
            code,
            flags=re.DOTALL
        )

    # Inyectar menú multicartera limpio si existe bloque de carteras
    if "CONFIGURACIÓN DE CARTERAS" in code:
        # Reemplazar bloque de carteras antiguo por el nuevo estructurado
        code = re.sub(
            r'💳 CONFIGURACIÓN DE CARTERAS DE RECEPCIÓN.*?(?=\n\n|\n[a-zA-Z_#]|\Z)',
            WALLET_MENU_CODE.strip(),
            code,
            flags=re.DOTALL
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Validar sintaxis inmediatamente
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"  ✅ {file_path} compilado SIN ERRORES de sintaxis.")
    except py_compile.PyCompileError as e:
        print(f"  ❌ Error sintáctico en {file_path}:\n{e}")

print("================================================================================")
print("✅ REPARACIÓN FINALIZADA. LISTO PARA EJECUTAR ccia1 -> Opción 4.")
print("================================================================================")
