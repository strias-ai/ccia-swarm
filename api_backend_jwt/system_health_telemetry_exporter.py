# -*- coding: utf-8 -*-
"""
CCIA SYSTEM HEALTH TELEMETRY EXPORTER v1.0
Consolida métricas de sistema, base de datos y estado de artefactos para Opción 12.
"""
import os
import json
import psutil

def collect_telemetry_snapshot() -> dict:
    cpu_pct = psutil.cpu_percent(interval=0.1)
    ram_pct = psutil.virtual_memory().percent
    disk_pct = psutil.disk_usage("/").percent

    registry_path = os.path.join(os.path.dirname(__file__), "module_registry.json")
    active_modules = 0
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                reg_data = json.load(f)
                active_modules = len(reg_data.get("extensions", {}))
        except Exception:
            pass

    return {
        "status": "HEALTHY" if cpu_pct < 90.0 and ram_pct < 90.0 else "DEGRADED",
        "cpu_percent": cpu_pct,
        "ram_percent": ram_pct,
        "disk_percent": disk_pct,
        "active_modules": active_modules
    }

if __name__ == "__main__":
    snapshot = collect_telemetry_snapshot()
    print(f"📊 Telemetría Dashboard: Estado={snapshot['status']} | CPU={snapshot['cpu_percent']}% | RAM={snapshot['ram_percent']}% | Módulos={snapshot['active_modules']}")
