# -*- coding: utf-8 -*-
"""
CCIA RATE LIMITER SENTINEL v1.0
Protección contra inyección y ráfagas masivas mediante Token Bucket (Opción 3).
"""
import time

class RateLimiter:
    def __init__(self, capacity: int = 10, fill_rate: float = 2.0):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.fill_rate = fill_rate
        self.last_update = time.time()

    def allow(self, tokens_requested: int = 1) -> bool:
        now = time.time()
        delta = now - self.last_update
        self.last_update = now
        self.tokens = min(self.capacity, self.tokens + delta * self.fill_rate)
        
        if self.tokens >= tokens_requested:
            self.tokens -= tokens_requested
            return True
        return False

limiter = RateLimiter()

def check_rate_limit() -> dict:
    allowed = limiter.allow()
    return {"allowed": allowed, "remaining_tokens": round(limiter.tokens, 2)}

if __name__ == "__main__":
    print(f"🛡️ Rate Limiter Status: {check_rate_limit()}")
