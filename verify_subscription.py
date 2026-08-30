from fastapi import FastAPI, HTTPException, Header
import sqlite3

app = FastAPI(title="CCIA Subscription Guard")
DB_PATH = "/home/k1/ccia_workspace/university.db"

def check_user_subscription(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM user_subscriptions WHERE user_email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 'active'

@app.get("/v1/premium/content")
def get_premium_content(x_user_email: str = Header(..., alias="X-User-Email")):
    if not check_user_subscription(x_user_email):
        raise HTTPException(status_code=403, detail="Acceso denegado: Requiere suscripción activa.")
    
    return {
        "status": "access_granted",
        "user": x_user_email,
        "content": "🎓 Material exclusivo CCIA Monetización v1.0"
    }
