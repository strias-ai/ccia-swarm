"""
CCiA Tool Bus Client v2.0 - Conector Unificado con Sandbox VANT & AST
Artefactos 62, 63, 64, 65
"""

import json
import urllib.request
import urllib.parse
import ast
import sys
import subprocess
import tempfile
import os

try:
    import esprima
    HAS_ESPRIMA = True
except ImportError:
    HAS_ESPRIMA = False

GATEWAY_URL = "http://127.0.0.1:8065"

class CCiAToolBusClient:
    def __init__(self, gateway_url=GATEWAY_URL):
        self.gateway_url = gateway_url

    def parse_python_ast(self, code_str):
        """Analiza sintaxis y árbol AST de código Python."""
        try:
            tree = ast.parse(code_str)
            nodes = sum(1 for _ in ast.walk(tree))
            return {"valid": True, "language": "python", "total_ast_nodes": nodes, "error": None}
        except SyntaxError as e:
            return {"valid": False, "language": "python", "error": f"Line {e.lineno}: {e.msg}"}

    def parse_js_ast(self, code_str):
        """Analiza sintaxis y árbol AST de código JavaScript usando Esprima."""
        if HAS_ESPRIMA:
            try:
                parsed = esprima.parseScript(code_str)
                return {"valid": True, "language": "javascript", "ast_type": parsed.type, "body_length": len(parsed.body), "error": None}
            except Exception as e:
                return {"valid": False, "language": "javascript", "error": str(e)}
        return {"valid": False, "language": "javascript", "error": "Librería 'esprima' no disponible"}

    def run_in_sandbox(self, code_str, language="python", timeout_sec=5):
        """Ejecuta código de forma aislada en la Sandbox VANT para validar ejecución real."""
        if language in ["python", "py"]:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
                f.write(code_str)
                tmp_name = f.name
            try:
                res = subprocess.run([sys.executable, tmp_name], capture_output=True, text=True, timeout=timeout_sec)
                os.remove(tmp_name)
                return {
                    "success": res.returncode == 0,
                    "returncode": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip()
                }
            except subprocess.TimeoutExpired:
                if os.path.exists(tmp_name): os.remove(tmp_name)
                return {"success": False, "returncode": -1, "stdout": "", "stderr": "Execution Timeout (Sandbox)"}
            except Exception as e:
                if os.path.exists(tmp_name): os.remove(tmp_name)
                return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e)}
        return {"success": False, "returncode": -1, "stdout": "", "stderr": f"Lenguaje '{language}' no soportado en Sandbox local"}

    def is_gateway_online(self):
        """Verifica si el Gateway del Artefacto 65 responde en el puerto 8065."""
        try:
            req = urllib.request.Request(f"{self.gateway_url}/health", headers={"User-Agent": "CCiA-Artifact-Client"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

if __name__ == "__main__":
    client = CCiAToolBusClient()
    sb_test = client.run_in_sandbox("print('Sandbox VANT Operativa')")
    print(f"  [+] Test Sandbox VANT: {sb_test}")
