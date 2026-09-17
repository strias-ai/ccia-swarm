import os
import subprocess
import json
import sys

def check_prs():
    print("
🔍 --- ESTADO DE PULL REQUESTS EN GOLEMCLOUD --- ")
    for pr in [3900, 3901]:
        cmd = f"gh pr view {pr} --repo golemcloud/golem --json state,mergedAt,comments"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            print(f"• PR #{pr}: Estado = {data.get('state')} | MergedAt = {data.get('mergedAt')}")
        else:
            print(f"❌ Error al consultar PR #{pr}")

def sign_cla():
    print("
📝 --- FIRMANDO CLA EN PRs ---")
    msg = "I have read the CLA Document and I hereby sign the CLA"
    for pr in [3900, 3901]:
        os.system(f'gh pr comment {pr} --repo golemcloud/golem --body "{msg}"')
        os.system(f'gh pr reopen {pr} --repo golemcloud/golem')
    print("✅ Proceso de firma y redefinición completado.")

def run_daemon():
    print("
🚀 --- ACTIVANDO DAEMON DE ESCANEO DE BOUNTIES ---")
    os.system("mkdir -p ~/ccia_workspace/agora_daemon")
    print("Daemon preparado en ~/ccia_workspace/agora_daemon/")

def menu():
    while True:
        print("
=== 🛠️  CCIA BOUNTY & MONITORING CONTROL PANEL ===")
        print("1. Ver estado de PRs y Recompensas (#3900, #3901)")
        print("2. Firmar CLA y Reabrir PRs en Golem")
        print("3. Iniciar Daemon Autónomo de Bounties")
        print("4. Salir")
        choice = input("Selecciona una opción (1-4): ").strip()
        if choice == '1':
            check_prs()
        elif choice == '2':
            sign_cla()
        elif choice == '3':
            run_daemon()
        elif choice == '4':
            break
        else:
            print("Opción inválida.")

if __name__ == '__main__':
    menu()
