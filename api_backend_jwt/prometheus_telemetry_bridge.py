# -*- coding: utf-8 -*-
"""
CCIA PROMETHEUS TELEMETRY BRIDGE v1.0
Exposición de Métricas Estándar OpenTelemetry / Prometheus para Grafana (Opción 12).
"""
import psutil

def export_prometheus_format() -> str:
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    return f"""# HELP ccia_cpu_usage_percent Porcentaje de uso de CPU
# TYPE ccia_cpu_usage_percent gauge
ccia_cpu_usage_percent {cpu}
# HELP ccia_ram_usage_percent Porcentaje de uso de memoria RAM
# TYPE ccia_ram_usage_percent gauge
ccia_ram_usage_percent {ram}
# HELP ccia_system_status Estado de salud (1=OK, 0=DEGRADED)
# TYPE ccia_system_status gauge
ccia_system_status {1.0 if cpu < 90.0 and ram < 90.0 else 0.0}
"""

if __name__ == "__main__":
    print("📊 Formato Exportable Prometheus:")
    print(export_prometheus_format().strip())
