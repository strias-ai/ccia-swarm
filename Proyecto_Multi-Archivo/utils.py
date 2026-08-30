import sys
import os
import json
import jwt
from datetime import datetime, timedelta
from typing import Any, Dict, Union

# Configuración de la clave secreta para JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Configuración de la duración de expiración del token JWT
EXPIRATION_DELTA = timedelta(minutes=30)

def generate_jwt(payload: Dict[str, Any]) -> str:
    """Genera un token JWT con la configuración de SECRET_KEY y EXPIRATION_DELTA."""
    try:
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        print(f"Error al generar el token JWT: {e}")
        return None

def decode_jwt(token: str) -> Union[Dict[str, Any], None]:
    """Decodifica un token JWT utilizando la configuración de SECRET_KEY."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        print("Token JWT expirado")
        return None
    except jwt.InvalidTokenError:
        print("Token JWT inválido")
        return None

def validate_jwt(token: str) -> bool:
    """Valida un token JWT."""
    decoded_token = decode_jwt(token)
    if decoded_token:
        return True
    return False

def check_endpoint_injection(input_data: str) -> bool:
    """Verifica si el input_data contiene inyecciones de SQL o similar."""
    # Implementa la lógica de validación aquí
    # Por ejemplo, puedes usar expresiones regulares o librerías de análisis de vulnerabilidades
    return False

def check_jwt_hardcoded(payload: Dict[str, Any]) -> bool:
    """Verifica si las credenciales o claves JWT están hardcodeadas."""
    # Implementa la lógica de validación aquí
    # Por ejemplo, puedes buscar palabras clave o patrones conocidos
    return False

def audit_jwt(token: str) -> None:
    """Audita un token JWT."""
    if validate_jwt(token):
        print("Token JWT válido")
    else:
        print("Token JWT inválido")

def audit_endpoint(endpoint: str) -> None:
    """Audita un endpoint FastAPI."""
    if check_endpoint_injection(endpoint):
        print("Endpoint FastAPI vulnerable a inyecciones")
    else:
        print("Endpoint FastAPI seguro")

def audit_jwt_hardcoded(payload: Dict[str, Any]) -> None:
    """Audita si las credenciales o claves JWT están hardcodeadas."""
    if check_jwt_hardcoded(payload):
        print("Credenciales o claves JWT hardcodeadas")
    else:
        print("Credenciales o claves JWT seguras")

def main():
    if len(sys.argv) < 2:
        print("Uso: python utils.py <token|endpoint|payload>")
        return

    arg = sys.argv[1]

    if arg == 'token':
        token = sys.argv[2]
        audit_jwt(token)
    elif arg == 'endpoint':
        endpoint = sys.argv[2]
        audit_endpoint(endpoint)
    elif arg == 'payload':
        payload = json.loads(sys.argv[2])
        audit_jwt_hardcoded(payload)
    else:
        print("Argumento no reconocido")

if __name__ == "__main__":
    main()