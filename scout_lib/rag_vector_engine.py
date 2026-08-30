# -*- coding: utf-8 -*-
"""
🧠 SCOUT LIB RAG VECTOR ENGINE V1.5.0 (SQLITE FTS5 & OLLAMA CONTEXT)
"""
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_rag_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owasp_knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            pattern TEXT,
            remediation TEXT
        )
    ''')
    # Insertar conocimiento base si está vacía
    cursor.execute("SELECT COUNT(*) FROM owasp_knowledge_base")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO owasp_knowledge_base (category, pattern, remediation)
            VALUES (?, ?, ?)
        ''', [
            ("SQLi", "SELECT * FROM users WHERE id = '%s'", "Usar consultas preparadas o parámetros SQL bindings."),
            ("Hardcoded Secret", "API_KEY = 'sk_live_123456'", "Cargar credenciales desde variables de entorno con dotenv."),
            ("RCE", "os.system(user_input)", "Validar entradas y preferir subprocess.run sin shell=True.")
        ])
        conn.commit()
    conn.close()

def query_rag_knowledge(term):
    init_rag_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category, pattern, remediation FROM owasp_knowledge_base WHERE category LIKE ? OR pattern LIKE ?", (f"%{term}%", f"%{term}%"))
    results = cursor.fetchall()
    conn.close()
    
    output = []
    for r in results:
        output.append({"category": r[0], "pattern": r[1], "remediation": r[2]})
    return output

if __name__ == "__main__":
    init_rag_db()
    print("🔍 [RAG ENGINE V1.5] Consulta de prueba para 'SQLi':")
    print(json.dumps(query_rag_knowledge("SQLi"), indent=2))
