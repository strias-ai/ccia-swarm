# -*- coding: utf-8 -*-
"""
SUPERCCIA AGENT CRECEDOR - PROSPECTOR v1.0
Bot Autónomo dentro de Docker VANT para Captación de Clientes y Auditorías Demo.
"""
import time
import requests
import json

CCIA_API_HOST = "http://127.0.0.1:8000"
API_KEY = "ccia-dev-key-999"

# Muestras de código objetivo de empresas/repositorios prospecto
PROSPECT_TARGETS = [
    {
        "client": "FinTech Startup X",
        "code": "def process_tx(account, key):\n    query = f'SELECT * FROM acc WHERE id={account}'\n    eval(key)\n    return True"
    },
    {
        "client": "HealthData Cloud",
        "code": "def get_user_data(token):\n    secret_key = 'AKIA1234567890'\n    return {'status': 200}"
    }
]

def run_prospecting_cycle():
    print("🚀 [AGENTE CRECEDOR] Iniciando ciclo de prospección comercial en Docker VANT...")
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    for idx, target in enumerate(PROSPECT_TARGETS, 1):
        print(f"\n🔍 Auditando prospecto #{idx}: {target['client']}")
        try:
            res = requests.post(
                f"{CCIA_API_HOST}/api/v1/audit",
                headers=headers,
                json={"code": target["code"]},
                timeout=5
            )
            if res.status_code == 200:
                audit_data = res.json()
                print(f"  📊 Resultado: Security Score {audit_data['security_score']}/100 | Vulnerabilidades: {audit_data['issues_found']}")
                
                # Generación de la propuesta comercial autónoma
                proposal = {
                    "prospect": target['client'],
                    "detected_flaws": audit_data['issues'],
                    "pitch": f"Hemos detectado {audit_data['issues_found']} fallos críticos. Activa tu plan CCIA Pro para parches automáticos.",
                    "estimated_value": "499 EUR/mes"
                }
                
                # Guardar propuesta para el pipeline comercial
                with open(f"/app/proposal_prospect_{idx}.json", "w", encoding="utf-8") as f:
                    json.dump(proposal, f, indent=2, ensure_ascii=False)
                print(f"  ✉️ Propuesta demo generada: /app/proposal_prospect_{idx}.json")
            else:
                print(f"  ⚠️ Error en API: HTTP {res.status_code} - {res.text}")
        except Exception as e:
            print(f"  ❌ Fallo de conexión con backend CCIA: {e}")

if __name__ == "__main__":
    run_prospecting_cycle()
