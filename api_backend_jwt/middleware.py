# -*- coding: utf-8 -*-
import time
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from collections import defaultdict

logger = logging.getLogger("api_resilience")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

class RateLimitAndLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        # Limpiar peticiones antiguas
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window_seconds]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            log_payload = {
                "timestamp": now,
                "event": "rate_limit_exceeded",
                "client_ip": client_ip,
                "path": request.url.path
            }
            logger.warning(json.dumps(log_payload))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Límite de peticiones superado. Reintente en unos segundos."
            )
            
        self.requests[client_ip].append(now)
        
        start_time = time.time()
        response = await call_next(request)
        process_time = round((time.time() - start_time) * 1000, 2)
        
        log_payload = {
            "timestamp": now,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "client_ip": client_ip,
            "latency_ms": process_time
        }
        logger.info(json.dumps(log_payload))
        return response
