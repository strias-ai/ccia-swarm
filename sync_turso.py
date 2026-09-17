import libsql_experimental as libsql
import sqlite3
import os

TURSO_URL = "https://ccia-strias-ai.aws-eu-west-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODk2MDE2NzcsImlkIjoiMDFhMGFjOGMtNzIwMS03ZDU5LTgwMjEtMDQ2OWU4Mjc2NTA3Iiwia2lkIjoiekpxNVlGbnFIMmh0N0s1YWY2TmV2UWZwSmN4WXNydllQaHRSaG5OVVQ0SSIsInJpZCI6IjczYzg1NGViLWQyNTgtNGI3Zi1hMDgyLTY5NmFlNTIxZTZmMCJ9.-5RVbtVLugf111qJfAT0nse1wiHLbPniR18MxfKNmzmuOpG9uysELWISQwCPiR6K6Cu1cd2VUu53dQ4-fD9tBA"
LOCAL_DB = "/home/k1/university.db"

def sync():
    try:
        cloud_conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cur_cloud = cloud_conn.cursor()
        
        local_conn = sqlite3.connect(LOCAL_DB)
        local_cur = local_conn.cursor()
        
        # Sincronizar Bounties
        bounties = local_cur.execute("SELECT title, reward, status, repository, source, url FROM bounty_opportunities").fetchall()
        for b in bounties:
            cur_cloud.execute('''
                INSERT OR IGNORE INTO bounty_opportunities (title, reward, status, repository, source, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', b)
            
        # Sincronizar Clientes API
        clients = local_cur.execute("SELECT client_name, email, api_key, tier, status FROM api_clients").fetchall()
        for c in clients:
            cur_cloud.execute('''
                INSERT OR IGNORE INTO api_clients (client_name, email, api_key, tier, status)
                VALUES (?, ?, ?, ?, ?)
            ''', c)
            
        # Sincronizar Telemetría
        telemetry = local_cur.execute("SELECT agent_name, event_type, payload FROM vant_agent_telemetry").fetchall()
        for t in telemetry:
            cur_cloud.execute('''
                INSERT OR IGNORE INTO vant_agent_telemetry (agent_name, event_type, payload)
                VALUES (?, ?, ?)
            ''', t)

        cloud_conn.commit()
        local_conn.close()
        print("☁️ [TURSO AUTO-SYNC] Sincronización con la nube completada.")
    except Exception as e:
        print(f"⚠️ [TURSO AUTO-SYNC ERROR] {e}")

if __name__ == "__main__":
    sync()
