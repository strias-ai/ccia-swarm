# -*- coding: utf-8 -*-
"""
CCIA WEBSOCKET EVENT STREAMER v1.0
Transmite métricas y eventos internos del CLI hacia el Web Dashboard en tiempo real.
"""
import json
import urllib.request

DASHBOARD_EVENT_URL = "http://127.0.0.1:8090/api/events"

def broadcast_event(event_type: str, data: dict) -> bool:
    """Envía telemetría al endpoint local de eventos."""
    payload = json.dumps({"event": event_type, "data": data}).encode("utf-8")
    req = urllib.request.Request(
        DASHBOARD_EVENT_URL, 
        data=payload, 
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False

if __name__ == "__main__":
    ok = broadcast_event("CLI_PING", {"status": "online"})
    print(f"📡 Event Streamer Ping: {'Éxito' if ok else 'Dashboard Off'}")
