from middleware import RateLimitAndLogMiddleware
# -*- coding: utf-8 -*-
import sys, os

# Forzar precedencia de paquetes de usuario sobre paquetes del sistema (/usr/lib/python3/dist-packages)
user_site = os.path.expanduser("~/.local/lib/python3.12/site-packages")
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User
from schemas import UserCreate, UserResponse, Token
from auth import get_password_hash, verify_password, create_access_token
from items import router as items_router
from logging_config import logger

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(RateLimitAndLogMiddleware)
# title="CCIA Backend API JWT", version="1.0.0")
app.include_router(items_router)

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    hashed_pwd = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Nuevo usuario registrado: {new_user.email}")
    return new_user

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Intento fallido de login para: {form_data.username}")
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Login exitoso: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"status": "online", "system": "CCIA v14.0 API REST Backend"}


@app.get('/health', tags=['System'])
def health_check():
    from telemetry_daemon import collect_metrics
    metrics = collect_metrics()
    return {
        'status': 'healthy',
        'system_metrics': metrics
    }
