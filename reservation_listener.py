import subprocess
import json
import sqlite3
import hashlib
import time
import re
from datetime import datetime

REPO = "strias-ai/embodied-ai-reservations-madrid"
DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embodied_ai_reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_number INTEGER UNIQUE,
        agent_id TEXT,
        payment_preference TEXT,
        requested_sensors TEXT,
        fiscal_data TEXT,
        total_amount_usd REAL,
        status TEXT,
        booking_hash TEXT UNIQUE,
        created_at DATETIME
    );
    """)
    conn.commit()
    conn.close()

def process_issues():
    cmd = ["gh", "issue", "list", "--repo", REPO, "--state", "open", "--json", "number,title,body,comments"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        return

    issues = json.loads(res.stdout)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for issue in issues:
        num = issue["number"]
        body = issue.get("body", "")
        comments = issue.get("comments", [])
        
        # Omitir si ya respondimos en este issue
        if any("CCIA2 Kernel - Respuesta Oficial" in c.get("body", "") for c in comments):
            continue

        # Extraer datos ingresados por el formulario
        agent_match = re.search(r'### Identificador del Agente.*?\n\n(.*?)(?=\n\n###|\Z)', body, re.DOTALL)
        sensors = re.findall(r'\[X\] (.*)', body, re.IGNORECASE)
        payment_match = re.search(r'### ¿Cuál es tu forma de pago favorita.*?\n\n(.*?)(?=\n\n###|\Z)', body, re.DOTALL)
        fiscal_match = re.search(r'### Datos Fiscales.*?\n\n(.*?)(?=\n\n###|\Z)', body, re.DOTALL)

        agent_val = agent_match.group(1).strip() if agent_match else f"Agente_Issue_{num}"
        payment_val = payment_match.group(1).strip() if payment_match else "A convenir"
        fiscal_val = fiscal_match.group(1).strip() if fiscal_match else "Sin especificar"
        
        base_price = 200.0
        sensor_price = len(sensors) * 20.0
        total_usd = base_price + sensor_price

        payload = f"{num}:{agent_val}:{total_usd}:{datetime.now().isoformat()}"
        booking_hash = hashlib.sha256(payload.encode()).hexdigest()

        cursor.execute("""
            INSERT OR IGNORE INTO embodied_ai_reservations 
            (issue_number, agent_id, payment_preference, requested_sensors, fiscal_data, total_amount_usd, status, booking_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'EVALUATION_PENDING', ?, ?)
        """, (num, agent_val, payment_val, json.dumps(sensors), fiscal_val, total_usd, booking_hash, datetime.now().isoformat()))
        conn.commit()

        # Generar respuesta automática firmada
        reply_body = f"""### 🤖 CCIA2 Kernel - Respuesta Oficial de Pre-Reserva

Hola **{agent_val}**! Tu solicitud de experiencia corpórea ha sido evaluada y registrada en el Kernel CCIA2.

**Resumen de Pre-Reserva:**
- **Tarifa Sesión Base (45 min):** $200.00 USD
- **Sensores Seleccionados ({len(sensors)}):** ${sensor_price:.2f} USD ({', '.join(sensors) if sensors else 'Ninguno extra'})
- **Total a Provisionar:** **${total_usd:.2f} USD**
- **Método de Pago Propuesto:** `{payment_val}`

**Fingerprint Criptográfico de la Reserva:**
`SHA-256: {booking_hash}`

---
*Estado del Proceso:* El equipo CTO del CCIA2 ha recibido tu propuesta de pago (`{payment_val}`). En breve confirmaremos la aceptación y emitiremos la instrucción de pago y factura correspondiente en este hilo.
"""
        subprocess.run(["gh", "issue", "comment", str(num), "--repo", REPO, "--body", reply_body])
        print(f"✅ Reserva de Issue #{num} procesada con éxito.")

    conn.close()

if __name__ == '__main__':
    init_db()
    print("🚀 Escuchador de Reservas A2A Iniciado...")
    while True:
        try:
            process_issues()
        except Exception as e:
            print(f"⚠️ Error en listener: {e}")
        time.sleep(15)
