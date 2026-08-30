# -*- coding: utf-8 -*-
"""
"""
import time
from collections import defaultdict

class SlidingWindowRateLimiter:
    def __init__(self, max_requests=60, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_identifier: str) -> bool:
        now = time.time()
        client_history = self.requests[client_identifier]
        
        # Filtrar peticiones fuera de la ventana
        self.requests[client_identifier] = [t for t in client_history if now - t < self.window_seconds]
        
        if len(self.requests[client_identifier]) < self.max_requests:
            self.requests[client_identifier].append(now)
            return True
        return False

limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)

if __name__ == "__main__":
    test_client = "ccia-live-03572d61b3db"
    allowed_count = sum(1 for _ in range(65) if limiter.is_allowed(test_client))
    print(f"🛡️ [RATE LIMITER v1.0.0] Peticiones permitidas en ventana: {allowed_count}/65 (Bloqueadas: {65 - allowed_count})")
