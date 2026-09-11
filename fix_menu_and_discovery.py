import py_compile
import os

# 1. Vincular el ejecutable art_63.py con el menú interactivo ccia_mando_63.py
mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"
art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

mando_launcher_code = '''
import sys
import os

sys.path.append("/home/k1/ccia_workspace/modules")
from art_63 import TriSwarmOrchestrator

def show_mando_menu():
    orch = TriSwarmOrchestrator()
    while True:
        print("""
================================================================================
  CENTRO DE MANDO Y CONTROL: SUPER ENJAMBRE ARTEFACTO 63 & 62
================================================================================
  [1] 📋 Ver Bounties Registrados y Estado de Ingesta (Art. 62)
  [2] 👑 Ejecutar Filtro Reina Antispam / Honeypot sobre Bounties
  [3] 🚀 Lanzar Ejecución Completa Tri-Enjambre con Supervisión Reina
  [4] 🎯 Procesar Siguiente Bounty Pendiente
  [5] 💳 Verificar Carteras de Cobro (Lightning / EVM)
  [0] 🚪 Salir al Submenú
=================================================================================""")
        op = input("CCiA-Mando-63> ").strip()
        if op == "1":
            targets = orch.fetch_pending_bounties_from_db()
            print(f"\n📋 Total Bounties Pendientes en DB: {len(targets)}")
            for t in targets:
                print(f"  - {t[0]}#{t[1]}: {t[2]}")
        elif op == "2":
            print("\n👑 Auditando filtro Antispam / Honeypot con la Reina...")
            targets = orch.fetch_pending_bounties_from_db()
            for t in targets:
                check_prompt = f"Evaluar viabilidad del issue {t[0]}#{t[1]} ('{t[2]}'). Responder JSON: {{\\\"valid\\\": true, \\\"reason\\\": \\\"...\\\"}}"
                res = orch.call_ollama_direct(orch.queen_brains[0]["model"], orch.queen_brains[0]["role"], check_prompt)
                valid, reason = orch.validate_antispam_output(res)
                status = "✅ VÁLIDO" if valid else "🛑 SPAM/TRAMPA"
                print(f"  [{status}] {t[0]}#{t[1]} -> {reason}")
        elif op == "3" or op == "4":
            orch.run_full_pipeline()
        elif op == "5":
            print(f"\n💳 Carteras Configuradas:\n  ⚡ Lightning: {orch.wallets['lightning']}\n  🔗 EVM: {orch.wallets['evm']}")
        elif op == "0":
            break

if __name__ == "__main__":
    show_mando_menu()
'''

with open(mando_path, "w", encoding="utf-8") as f:
    f.write(mando_launcher_code)

# 2. Asegurar que modules/art_63.py invoque show_mando_menu() al ejecutarse directamente
with open(art63_path, "r", encoding="utf-8", errors="ignore") as f:
    art_content = f.read()

if "if __name__ ==" in art_content:
    art_content = art_content[:art_content.find("if __name__ ==")]

art_content += '''
if __name__ == "__main__":
    import ccia_mando_63
    ccia_mando_63.show_mando_menu()
'''

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(art_content)

py_compile.compile(mando_path, doraise=True)
py_compile.compile(art63_path, doraise=True)
print("✅ Menú de Mando y Control 63 reestructurado y compìlado con éxito.")
