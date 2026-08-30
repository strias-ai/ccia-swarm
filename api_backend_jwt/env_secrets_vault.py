# -*- coding: utf-8 -*-
"""
CCIA ENV SECRETS VAULT v1.0
Auditá variables de entorno y enmascara secretos en logs y telemetría.
"""
import os
import re

SENSITIVE_KEYS = ["JWT_SECRET", "DATABASE_URL", "API_KEY", "PASSWORD"]

def mask_secret(value: str) -> str:
    if not value or len(value) <= 6:
        return "******"
    return value[:3] + "..." + value[-3:]

def audit_environment_secrets() -> dict:
    audited = {}
    for key in SENSITIVE_KEYS:
        val = os.getenv(key)
        if val:
            audited[key] = mask_secret(val)
        else:
            audited[key] = "NOT_SET"
    return audited

if __name__ == "__main__":
    res = audit_environment_secrets()
    print(f"🔒 Status Bóveda de Secretos: {res}")
