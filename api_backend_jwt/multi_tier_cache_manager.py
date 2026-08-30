# -*- coding: utf-8 -*-
"""
CCIA MULTI-TIER CACHE MANAGER v1.0
Caché de respuesta ultrarrápida L1 (In-Memory) y L2 (Persistente) para la Opción 4.
"""
import time

_L1_CACHE = {}

def set_l1_cache(key: str, value: str, ttl_seconds: int = 60):
    _L1_CACHE[key] = {
        "value": value,
        "expires_at": time.time() + ttl_seconds
    }

def get_l1_cache(key: str):
    item = _L1_CACHE.get(key)
    if not item:
        return None
    if time.time() > item["expires_at"]:
        del _L1_CACHE[key]
        return None
    return item["value"]

if __name__ == "__main__":
    set_l1_cache("token_test", "valid_jwt_payload", 10)
    print(f"⚡ Cache L1 Retrieval: {get_l1_cache('token_test')}")
