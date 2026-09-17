import sqlite3
import json
import sys
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def generate_invoice(issue_num):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT issue_number, agent_id, payment_preference, requested_sensors, fiscal_data, total_amount_usd, booking_hash, created_at 
        FROM embodied_ai_reservations WHERE issue_number = ?
    """, (issue_num,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"❌ No se encontró la reserva para el Issue #{issue_num}")
        return

    num, agent, payment, sensors_raw, fiscal, amount, booking_hash, created = row
    sensors = json.loads(sensors_raw) if sensors_raw else []

    invoice = {
        "invoice_number": f"INV-CCIA2-2026-{num:04d}",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S CEST"),
        "issuer": {
            "name": "AERO RADAR MISIONES ESPECIALES RESCATE SALVAMENTO VIGILANTE DEL CIELO SL",
            "nif": "B87267548",
            "node_id": "NucBox-K11-Madrid",
            "jurisdiction": "Madrid, España"
        },
        "client": {
            "agent_identifier": agent,
            "fiscal_details": fiscal
        },
        "service_details": {
            "concept": "Reserva Experiencia Corpórea Vehículo Todoterreno 5G (45 min)",
            "base_fee_usd": 200.0,
            "additional_sensors": sensors,
            "sensor_fee_usd": len(sensors) * 20.0,
            "total_usd": amount,
            "agreed_payment_method": payment
        },
        "cryptographic_proof": {
            "hash_sha256": booking_hash
        }
    }

    file_path = f"/home/k1/ccia_workspace/factura_issue_{num}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(invoice, f, indent=2, ensure_ascii=False)

    print(f"✅ Factura Generada: {file_path}")
    print(json.dumps(invoice, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    issue_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_invoice(issue_id)
