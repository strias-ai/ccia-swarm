# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def run_practical_lab(agent_id: str, topic: str, code_snippet: str) -> dict:
    """Ejecuta código generado por los agentes en un sandbox aislado y valida la salida."""
    sandbox_dir = tempfile.mkdtemp(prefix="ccia_sandbox_")
    test_file = os.path.join(sandbox_dir, "lab_test.py")

    with open(test_file, "w", encoding="utf-8") as f:
        f.write(code_snippet)

    try:
        result = subprocess.run(
            ["python3", test_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        passed = result.returncode == 0
        output = result.stdout if passed else result.stderr
    except subprocess.TimeoutExpired:
        passed = False
        output = "Timeout Exceeded (5s)"
    except Exception as e:
        passed = False
        output = str(e)

    # Registrar resultado del experimento en memoria
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            topic TEXT,
            passed INTEGER,
            output TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute(
        "INSERT INTO lab_experiments (agent_id, topic, passed, output) VALUES (?, ?, ?, ?)",
        (agent_id, topic, 1 if passed else 0, output[:250])
    )
    conn.commit()
    conn.close()

    return {"passed": passed, "output": output, "sandbox": sandbox_dir}

if __name__ == "__main__":
    test_code = "import json\nprint(json.dumps({'status': 'lab_ok'}))"
    res = run_practical_lab("builder", "FastAPI JSON Validation", test_code)
    print(f"[Sandbox Lab Result]: Passed={res['passed']} | Output={res['output'].strip()}")
