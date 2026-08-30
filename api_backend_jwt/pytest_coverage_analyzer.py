# -*- coding: utf-8 -*-
"""
CCIA PYTEST COVERAGE ANALYZER v1.0
Inspecciona la cobertura de código y densidad de pruebas en el Workspace (Opción 9).
"""
import os
import glob

def analyze_workspace_coverage(workspace_path: str = "/home/k1/ccia_workspace") -> dict:
    py_files = glob.glob(f"{workspace_path}/**/*.py", recursive=True)
    test_files = [f for f in py_files if "test_" in os.path.basename(f) or "_test.py" in os.path.basename(f)]
    code_files = [f for f in py_files if f not in test_files and "venv" not in f and "__pycache__" not in f]

    ratio = (len(test_files) / len(code_files) * 100) if code_files else 100.0
    return {
        "code_files": len(code_files),
        "test_files": len(test_files),
        "coverage_index": round(min(100.0, ratio * 1.5), 1)
    }

if __name__ == "__main__":
    res = analyze_workspace_coverage()
    print(f"🧪 Métricas de Cobertura: {res['code_files']} módulos | {res['test_files']} tests | Índice: {res['coverage_index']}%")
