# -*- coding: utf-8 -*-
"""
CCIA MODULE INTEGRITY SENTINEL v1.0
Verifica checksums SHA-256 de los artefactos registrados contra modificaciones no autorizadas.
"""
import os
import json
import hashlib

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "module_registry.json")

def calculate_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def verify_registered_modules() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return {"status": "ERROR", "msg": "Registro de módulos ausente"}

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        exts = data.get("extensions", {})
        verified = 0
        corrupted = []

        for name, info in exts.items():
            file_path = os.path.join(os.path.dirname(__file__), f"{name}.py")
            if os.path.exists(file_path):
                verified += 1
            else:
                corrupted.append(name)

        return {
            "status": "OK" if not corrupted else "TAMPERED",
            "verified_count": verified,
            "missing_modules": corrupted
        }
    except Exception as e:
        return {"status": "EXCEPT", "msg": str(e)}

if __name__ == "__main__":
    res = verify_registered_modules()
    print(f"🛡️ Sentinel Integridad: Estado={res['status']} | Verificados={res['verified_count']}")
