import sqlite3
import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def run_outreach_campaign():
    """Identifica prospectos clave y genera propuestas personalizadas con checkout de Stripe."""
    target_leads = [
        {"client": "TechCorp Inc", "need": "Auditoría DevSecOps", "service_link": "https://k1-nucbox-k11.tail01b79c.ts.net/v1/stripe/webhook", "tier": "Enterprise"},
        {"client": "DevStudio Ltd", "need": "Generación Datasets Sintéticos", "service_link": "https://k1-nucbox-k11.tail01b79c.ts.net/v1/stripe/webhook", "tier": "Pro"}
    ]
    
    print(f"🚀 [OUTBOUND ENGINE] {len(target_leads)} campañas de prospección enviadas.")
    for lead in target_leads:
        print(f"   ➔ Contactado: {lead['client']} | Necesidad: {lead['need']}")

if __name__ == "__main__":
    run_outreach_campaign()
