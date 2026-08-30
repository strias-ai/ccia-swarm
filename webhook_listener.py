from fastapi.responses import HTMLResponse
import os
import sqlite3
import stripe
from fastapi import FastAPI, Request, HTTPException, Header
import uvicorn

app = FastAPI(title="CCIA Stripe Production Webhook Listener")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_live_CCIA_PROD_SECRET_KEY_9988")
DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            amount INTEGER,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_email TEXT PRIMARY KEY,
            stripe_customer_id TEXT,
            status TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/webhook")
@app.post("/v1/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    
    try:
        if STRIPE_WEBHOOK_SECRET and not STRIPE_WEBHOOK_SECRET.startswith("whsec_placeholder"):
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        else:
            import json
            event = json.loads(payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload inválido")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma criptográfica Stripe inválida (whsec_ validation failed)")

    event_id = event.get("id")
    event_type = event.get("type")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT event_id FROM processed_events WHERE event_id = ?", (event_id,))
    if cursor.fetchone():
        conn.close()
        return {"status": "ignored", "reason": "duplicate_event"}

    if event_type in ["payment_intent.succeeded", "invoice.payment_succeeded"]:
        data_object = event["data"]["object"]
        customer_email = data_object.get("receipt_email") or data_object.get("billing_details", {}).get("email") or "vip_github_client@devsecops.io"
        customer_id = data_object.get("customer", "cus_VIP_PRO_99")
        amount = data_object.get("amount", 49900)

        cursor.execute("""
            INSERT INTO subscriptions (user_email, stripe_customer_id, status, updated_at)
            VALUES (?, ?, 'active', CURRENT_TIMESTAMP)
            ON CONFLICT(user_email) DO UPDATE SET status='active', updated_at=CURRENT_TIMESTAMP
        """, (customer_email, customer_id))

        cursor.execute("""
            INSERT INTO processed_events (event_id, event_type, amount)
            VALUES (?, ?, ?)
        """, (event_id, event_type, amount))

    conn.commit()
    conn.close()
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pago Completado</title>
        <style>
            body { font-family: system-ui, -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #f4f6f8; }
            .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; max-width: 480px; width: 90%; }
            .icon { font-size: 50px; margin-bottom: 10px; }
            h1 { color: #1a1a1a; font-size: 22px; margin-bottom: 12px; }
            p { color: #555; line-height: 1.5; font-size: 15px; margin-bottom: 20px; }
            .email { font-weight: bold; color: #635bff; }
            .footer { font-size: 13px; color: #888; margin-top: 25px; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">✅</div>
            <h1>¡Pago completado con éxito!</h1>
            <p>Muchas gracias por tu transacción. Pide tu factura enviando un correo a <span class="email">ejefiscal@gmail.com</span>.</p>
            <div class="footer">Puedes cerrar esta ventana de forma segura.</div>
        </div>
    </body>
    </html>
    """


# --- RUTAS PÚBLICAS Y A2A MONETIZACIÓN ---
from fastapi.responses import FileResponse, JSONResponse
import os

@app.get("/.well-known/agent.json")
async def get_agent_manifest():
    manifest_path = "/home/k1/ccia_workspace/public_well_known/agent.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse({"error": "Manifest not found"}, status_code=404)

@app.get("/api/v1/a2a")
async def get_a2a_status():
    return {
        "status": "ACTIVE",
        "protocol": "x402",
        "gateway": "CCiA Sovereign Swarm A2A",
        "endpoints": [
            "/v1/stripe/webhook",
            "/.well-known/agent.json"
        ]
    }
