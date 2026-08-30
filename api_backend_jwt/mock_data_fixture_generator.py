# -*- coding: utf-8 -*-
"""
CCIA MOCK DATA FIXTURE GENERATOR v1.0
Genera estructuras de datos ficticios y payloads sintéticos para tests en Opción 9.
"""
import random
import uuid

def generate_user_payload() -> dict:
    uid = str(uuid.uuid4())[:8]
    return {
        "username": f"test_user_{uid}",
        "email": f"user_{uid}@nucbox-k11.local",
        "role": random.choice(["admin", "developer", "auditor"]),
        "is_active": True
    }

def generate_token_payload() -> dict:
    return {
        "sub": str(uuid.uuid4()),
        "token_type": "bearer",
        "expires_in": 3600
    }

if __name__ == "__main__":
    print(f"🧪 Mock User Payload: {generate_user_payload()}")
    print(f"🔑 Mock Token Payload: {generate_token_payload()}")
