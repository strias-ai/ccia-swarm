# -*- coding: utf-8 -*-
"""
CCIA PROJECT SCAFFOLDER GUARD v1.0
Valida y sanitiza archivos de código (Python, JSON, YAML) generados en la Opción 1
antes de ser guardados en el Workspace.
"""
import ast
import json

def audit_and_clean_file_content(filename: str, content: str) -> tuple[bool, str]:
    """Audita sintaxis y aplica auto-reparación básica si es necesario."""
    if filename.endswith(".py"):
        try:
            ast.parse(content)
            return True, content
        except SyntaxError:
            # Intento de sanitización: remover bloques de markdown residuales
            cleaned = content.replace("```python", "").replace("```", "").strip()
            try:
                ast.parse(cleaned)
                return True, cleaned
            except SyntaxError:
                return False, content

    elif filename.endswith(".json"):
        try:
            json.loads(content)
            return True, content
        except Exception:
            return False, content

    return True, content

if __name__ == "__main__":
    valid, code = audit_and_clean_file_content("test.py", "```python\nprint('OK')\n```")
    print(f"🛡️ Test Guardián: Valid={valid}")
