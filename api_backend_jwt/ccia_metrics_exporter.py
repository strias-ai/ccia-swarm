# -*- coding: utf-8 -*-
"""
"""
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def export_metrics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM api_clients")
    total_clients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vant_agent_telemetry")
    total_telemetry = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ccia_artifact_manifests")
    total_artifacts = cursor.fetchone()[0]
    
    conn.close()
    
    return f"""# HELP ccia_total_clients Total registered API clients
# TYPE ccia_total_clients counter
ccia_total_clients {total_clients}

# HELP ccia_scouted_leads Total scouted telemetry leads
# TYPE ccia_scouted_leads counter
ccia_scouted_leads {total_telemetry}

# HELP ccia_certified_artifacts Total certified artifacts in DB
# TYPE ccia_certified_artifacts gauge
ccia_certified_artifacts {total_artifacts}
"""

if __name__ == "__main__":
    print("📊 [METRICS EXPORTER v1.0.0] Muestra de métricas Prometheus:")
    print(export_metrics())
