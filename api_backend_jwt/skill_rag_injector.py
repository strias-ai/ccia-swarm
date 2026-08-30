# -*- coding: utf-8 -*-
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def get_agent_knowledge_context(agent_id: str, max_items: int = 3) -> str:
    """Extrae las tesis aprobadas del agente para inyectarlas en su System Prompt."""
    if not os.path.exists(DB_PATH):
        return ""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT topic, summary FROM knowledge_vault WHERE agent_id = ? AND status = 'APPROVED' ORDER BY id DESC LIMIT ?",
        (agent_id, max_items)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return ""

    context_lines = [f"--- MEMORIA Y CONOCIMIENTO ADQUIRIDO DE {agent_id.upper()} ---"]
    for topic, summary in rows:
        context_lines.append(f"• [{topic}]: {summary}")
    context_lines.append("-------------------------------------------------------------")
    
    return "\n".join(context_lines)

if __name__ == "__main__":
    print(get_agent_knowledge_context("scout_lib"))
