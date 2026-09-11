import re

path = "/home/k1/ccia_workspace/api_backend_jwt/github_scout_agent.py"
with open(path, "r") as f:
    code = f.read()

if "403" not in code:
    old_error_block = 'print(json.dumps({"status": "ERROR", "detail": str(e)}))'
    new_error_block = '''if "403" in str(e):
        print("⏳ [GITHUB SCOUT] Cuota de Search API alcanzada (403). Pausando prospección hasta la siguiente ventana.")
    else:
        print(json.dumps({"status": "ERROR", "detail": str(e)}))'''
    code = code.replace(old_error_block, new_error_block)
    with open(path, "w") as f:
        f.write(code)
    print("✅ Parche de manejo de cuota GitHub API aplicado.")
else:
    print("ℹ️ El script ya cuenta con manejo de respuestas 403.")
