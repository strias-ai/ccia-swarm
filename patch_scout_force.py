import urllib.error

path = "/home/k1/ccia_workspace/api_backend_jwt/github_scout_agent.py"
with open(path, "r") as f:
    code = f.read()

# Reemplazar captura de excepciones genéricas por captura específica de HTTPError 403
old_pattern = "except Exception as e:"
new_pattern = """except urllib.error.HTTPError as e:
    if e.code == 403:
        print(json.dumps({"status": "RATE_LIMITED", "detail": "Search API quota window active (403). Waiting for next cycle."}))
    else:
        print(json.dumps({"status": "ERROR", "detail": str(e)}))
except Exception as e:"""

if "urllib.error.HTTPError" not in code:
    if "import urllib.request" in code and "import urllib.error" not in code:
        code = code.replace("import urllib.request", "import urllib.request\nimport urllib.error")
    code = code.replace(old_pattern, new_pattern)
    with open(path, "w") as f:
        f.write(code)
    print("✅ Parche de excepciones urllib.error.HTTPError aplicado a github_scout_agent.py.")
else:
    print("ℹ️ github_scout_agent.py ya contiene el manejador de HTTPError.")
