# -*- coding: utf-8 -*-
"""
CCIA HUMAN RESOURCE BROKER v1.0
Protocolo de solicitudes agente-humano para auto-riqueza y licencias (Opción 4).
"""
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_broker_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS human_resource_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            request_type TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            justification TEXT NOT NULL,
            estimated_roi TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_ticket(agent: str, req_type: str, resource: str, justification: str, roi: str) -> int:
    init_broker_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO human_resource_tickets (agent, request_type, resource_name, justification, estimated_roi)
        VALUES (?, ?, ?, ?, ?)
    ''', (agent, req_type, resource, justification, roi))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def list_pending_tickets() -> list:
    init_broker_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, agent, request_type, resource_name, justification, estimated_roi FROM human_resource_tickets WHERE status='PENDING'")
    rows = cursor.fetchall()
    conn.close()
    return rows

def resolve_ticket(ticket_id: int, approved: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    status = "APPROVED" if approved else "REJECTED"
    cursor.execute("UPDATE human_resource_tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_broker_db()
    tid = create_ticket(
        agent="Crecedor",
        req_type="SOFTWARE_DEP",
        resource="redis-server",
        justification="Habilitar caché de aceleración L2 para el Micro-SaaS de Auditoría AST",
        roi="150 EUR/mes estimación de ingresos para cubrir coste eléctrico"
    )
    print(f"🎫 Ticket #{tid} generado autónomamente.")
    print(f"📋 Tickets pendientes de revisión humana: {len(list_pending_tickets())}")
