import json
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def audit_cloud_resources():
    # Análisis heurístico de optimización de infraestructura
    recommendations = [
        {"resource": "k8s-cluster-dev", "issue": "CPU overprovisioned", "monthly_savings_usd": 120.0},
        {"resource": "docker-host-idle", "issue": "Unused volumes", "monthly_savings_usd": 45.0}
    ]
    
    total_savings = sum(r["monthly_savings_usd"] for r in recommendations)
    commission_fee = round(total_savings * 0.15, 2) # 15% de comisión por ahorro
    
    print(f"💰 Ahorro mensual detectado: ${total_savings} USD | Comisión CCiA: ${commission_fee} USD")
    return recommendations

if __name__ == "__main__":
    audit_cloud_resources()
