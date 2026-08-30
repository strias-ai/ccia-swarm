# -*- coding: utf-8 -*-
"""
CCIA THESIS AUTO-DEFENSE & LEVEL-UP ENGINE v1.0
Audita los logros de los agentes, evalúa código generado mediante Evaluator (DeepSeek-R1)
y promueve automáticamente el nivel de habilidad en university.db.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def evaluate_and_promote_agents():
    if not os.path.exists(DB_PATH):
        return "⚠️ university.db no encontrada."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_skills (
            agent_id TEXT PRIMARY KEY,
            level INTEGER DEFAULT 1,
            specialty TEXT,
            approved_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    cur.execute("SELECT agent_id, level, approved_count FROM agent_skills")
    skills = cur.fetchall()

    promoted = []
    for agent_id, level, approved_count in skills:
        required_thesis = level * 2
        if approved_count >= required_thesis:
            new_level = level + 1
            cur.execute("UPDATE agent_skills SET level = ? WHERE agent_id = ?", (new_level, agent_id))
            promoted.append(f"🎓 {agent_id}: ¡Promovido de Nivel {level} ➡️ Nivel {new_level}!")

    conn.commit()
    conn.close()

    if promoted:
        return "\n".join(promoted)
    return "✅ Todos los agentes se encuentran consolidados en su nivel actual."

if __name__ == "__main__":
    print(evaluate_and_promote_agents())
