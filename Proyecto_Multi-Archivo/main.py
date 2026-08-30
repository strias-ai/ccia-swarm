from api_key_monetization_guard import verify_api_key_middleware
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

app = FastAPI()
app.middleware("http")(verify_api_key_middleware)
# app = FastAPI()

# Configuración de la aplicación
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de cifrado para las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para generar un token JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token JWT
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = jwt.PyJWTAlgorithm(payload)
    except JWTError:
        raise credentials_exception

# Dependencia para autenticación
def get_current_user(form_data: OAuth2PasswordRequestForm = Depends()):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = verify_access_token(form_data.token, credentials_exception)
    return user

# Ruta de inicio
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI JWT Audit"}

# Ruta de login
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = pwd_context.verify(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Ruta protegida
@app.get("/protected")
async def read_protected(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}!"}
from router import router
app.include_router(router)
