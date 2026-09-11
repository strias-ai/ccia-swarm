#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
from pathlib import Path

DB_PATH = "/home/k1/ccia_workspace/m_learning_memory.db"

def init_vector_memory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_patches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT,
            issue_summary TEXT,
            ast_snippet TEXT,
            successful_patch TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hydrate_context(repo_path, file_target):
    """Extrae el contenido real del archivo afectado para dotar de ojos al enjambre."""
    full_path = Path(repo_path) / file_target
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        return "".join(lines[:150])
    return "Código fuente no disponible en disco local."

def query_m_learning(issue_summary):
    """Recupera parches pasados relevantes."""
    init_vector_memory()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT successful_patch FROM memory_patches WHERE issue_summary LIKE ? ORDER BY id DESC LIMIT 1", (f"%{issue_summary}%",))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Sin antecedentes en memoria m-learning."

def save_successful_patch(repo_name, issue_summary, ast_snippet, patch_code):
    """Guarda en la base de datos de aprendizaje m-learning las soluciones validadas."""
    init_vector_memory()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO memory_patches (repo_name, issue_summary, ast_snippet, successful_patch)
        VALUES (?, ?, ?, ?)
    ''', (repo_name, issue_summary, ast_snippet, patch_code))
    conn.commit()
    conn.close()

def process_task(task_payload):
    init_vector_memory()
    repo = task_payload.get("repo", "/home/k1/ccia_workspace")
    issue = task_payload.get("issue", "")
    target_file = task_payload.get("target_file", "")
    
    code_context = hydrate_context(repo, target_file)
    past_memory = query_m_learning(issue)
    
    enriched_prompt = f"""=== ENJAMBRE CCIA: CONTEXTO HIDRATADO ===
REPOSITORIO: {repo}
ISSUE: {issue}

--- CÓDIGO FUENTE REAL (AST / OJOS) ---
{code_context}

--- MEMORIA M-LEARNING (PATRONES PREVIOS) ---
{past_memory}
========================================="""
    return {
        "enriched_prompt": enriched_prompt,
        "ast_snippet": code_context
    }

if __name__ == "__main__":
    test_payload = {
        "repo": "/home/k1/ccia_workspace",
        "issue": "Fix typo in stripe sync",
        "target_file": "modules/stripe_live_sync.py"
    }
    res = process_task(test_payload)
    print("--- MIDDLEWARE ACTUALIZADO OK ---")
