# -*- coding: utf-8 -*-
"""
CCIA OLLAMA CIRCUIT BREAKER v1.0
Gestiona reintentos y fallbacks automáticos en caso de saturación o timeout de Ollama.
"""
import time
from typing import Callable, Any

class OllamaCircuitBreaker:
    def __init__(self, max_retries: int = 2, backoff_sec: float = 1.0):
        self.max_retries = max_retries
        self.backoff_sec = backoff_sec

    def execute_with_fallback(self, primary_fn: Callable[[], Any], fallback_fn: Callable[[], Any]) -> Any:
        for attempt in range(1, self.max_retries + 1):
            try:
                return primary_fn()
            except Exception as e:
                print(f"⚠️ [CIRCUIT BREAKER] Reintento {attempt}/{self.max_retries} tras error: {e}")
                time.sleep(self.backoff_sec)
        
        print("🚨 [CIRCUIT BREAKER] Límite alcanzado. Activando ruta de respaldo (Fallback)...")
        return fallback_fn()

if __name__ == "__main__":
    cb = OllamaCircuitBreaker()
    res = cb.execute_with_fallback(lambda: "OK Primario", lambda: "OK Fallback")
    print(f"🛡️ Estado Circuit Breaker: {res}")
