# -*- coding: utf-8 -*-
import sqlite3
import os
import traceback

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def record_error_autopsy(failed_agent: str, target_module: str, exception_obj: Exception):
    """Analiza una falla en tiempo de ejecución y programa una tarea de estudio prioritaria."""
    error_msg = str(exception_obj)
    tb_str = "".join(traceback.format_exception(type(exception_obj), exception_obj, exception_obj.__traceback__))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_autopsies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            module TEXT,
            error_msg TEXT,
            traceback TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute(
        "INSERT INTO error_autopsies (agent_id, module, error_msg, traceback) VALUES (?, ?, ?, ?)",
        (failed_agent, target_module, error_msg, tb_str)
    )

    # Programar tesis de remediación inmediata
    remediation_topic = f"Fix & Optimize: {target_module}"
    summary = f"Estudio reactivo tras fallo: {error_msg[:100]}"
    cursor.execute(
        "INSERT INTO knowledge_vault (agent_id, topic, source_url, summary, status) VALUES (?, ?, ?, ?, 'PENDING_REVIEW')",
        (failed_agent, remediation_topic, "https://docs.python.org/3/library/exceptions.html", summary)
    )
    
    conn.commit()
    conn.close()
    print(f"🚨 [AUTOPSIA DE ERROR] Registrado fallo en '{target_module}'. Tesis reactiva asignada a '{failed_agent}'.")

if __name__ == "__main__":
    try:
        1 / 0
    except Exception as e:
        record_error_autopsy("cleaner", "Math Operations Core", e)
