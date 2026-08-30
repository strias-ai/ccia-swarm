import sqlite3
from fastapi import FastAPI, HTTPException, Header, Depends

app = FastAPI(title="CCIA Monetized Core API v1.0", version="1.0.0")
DB_PATH = "/home/k1/ccia_workspace/university.db"

def verify_active_subscriber(x_user_email: str = Header(..., alias="X-User-Email")):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM user_subscriptions WHERE user_email = ?", (x_user_email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] != 'active':
        raise HTTPException(
            status_code=403, 
            detail={"error": "subscription_required", "message": "Acceso restringido a suscriptores activos."}
        )
    return x_user_email

@app.get("/v1/public/status")
def public_status():
    return {"status": "online", "access": "public"}

@app.get("/v1/premium/courses")
def get_premium_courses(user_email: str = Depends(verify_active_subscriber)):
    return {
        "status": "success",
        "authenticated_user": user_email,
        "premium_data": [
            {"id": "course_1", "title": "Arquitectura Avanzada de Microservicios & Systemd"},
            {"id": "course_2", "title": "Patrones de Idempotencia y Procesamiento de Eventos Stripe"}
        ]
    }


# --- VECTORES MONETIZADORES UNIFICADOS ---
try:
    from modules.github_fix_bot import router as fix_bot_router
    from modules.synthetic_data_api import router as datasets_router
    from modules.a2a_escrow_engine import router as escrow_router

    app.include_router(fix_bot_router, prefix="/v1/fix-bot", tags=["Vector 3: Fix-Bot"])
    app.include_router(datasets_router, prefix="/v1/datasets", tags=["Vector 4: Datasets"])
    app.include_router(escrow_router, prefix="/v1/a2a", tags=["Vector 6: A2A Escrow"])
except Exception as e:
    print(f"[CoreAPI Patch Warning] {e}")


# Router Anhydro-Vault API (Vector 4: Cold-State AI Agents)
try:
    from modules.anhydro_vault_api import router as anhydro_router
    app.include_router(anhydro_router, prefix="/v1/datasets/anhydro", tags=["Vector 4: Anhydro-Vault"])
except Exception as e:
    print(f"[API Patch Warning Anhydro] {e}")


# Route A2A Agent Manifest
from fastapi.responses import FileResponse
@app.get("/.well-known/agent.json")
async def get_a2a_agent_manifest():
    return FileResponse("/home/k1/ccia_workspace/public_well_known/agent.json", media_type="application/json")
