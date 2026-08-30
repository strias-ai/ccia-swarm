# -*- coding: utf-8 -*-
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def init_university_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            topic TEXT,
            source_url TEXT,
            summary TEXT,
            status TEXT DEFAULT 'PENDING_REVIEW',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_skills (
            agent_id TEXT PRIMARY KEY,
            level INTEGER DEFAULT 1,
            specialty TEXT,
            approved_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

class UniversityDean:
    def __init__(self):
        init_university_db()

    def submit_research(self, agent_id: str, topic: str, source_url: str, summary: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Comprobar memoria: ¿ya investigó este tema?
        cursor.execute("SELECT id FROM knowledge_vault WHERE agent_id = ? AND topic = ?", (agent_id, topic))
        if cursor.fetchone():
            conn.close()
            return f"[Decano] El agente '{agent_id}' ya tiene registrado el tema '{topic}' en memoria."

        cursor.execute(
            "INSERT INTO knowledge_vault (agent_id, topic, source_url, summary) VALUES (?, ?, ?, ?)",
            (agent_id, topic, source_url, summary)
        )
        conn.commit()
        conn.close()
        return f"[Decano] Tesis sobre '{topic}' recibida de '{agent_id}'."

    def evaluate_and_grade(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, agent_id, topic, summary FROM knowledge_vault WHERE status = 'PENDING_REVIEW'")
        pending = cursor.fetchall()
        
        results = []
        for item_id, agent_id, topic, summary in pending:
            status_update = "APPROVED" if len(summary) > 15 else "REJECTED"
            cursor.execute("UPDATE knowledge_vault SET status = ? WHERE id = ?", (status_update, item_id))
            
            if status_update == "APPROVED":
                # Memoria de Progresión: Actualizar o crear perfil del agente
                cursor.execute("SELECT level, approved_count FROM agent_skills WHERE agent_id = ?", (agent_id,))
                row = cursor.fetchone()
                if row:
                    lvl, count = row[0], row[1] + 1
                    new_lvl = lvl + 1 if count % 2 == 0 else lvl
                    cursor.execute("UPDATE agent_skills SET level = ?, approved_count = ? WHERE agent_id = ?", (new_lvl, count, agent_id))
                else:
                    cursor.execute("INSERT INTO agent_skills (agent_id, level, specialty, approved_count) VALUES (?, 1, ?, 1)", (agent_id, topic))
            
            results.append({"id": item_id, "agent": agent_id, "topic": topic, "status": status_update})
        
        conn.commit()
        conn.close()
        return results

if __name__ == "__main__":
    dean = UniversityDean()
    print("[Decano AI] Sistema de memoria persistente listo.")
