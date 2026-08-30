import py_compile

path = "/home/k1/ccia_workspace/api_backend_jwt/github_scout_agent.py"
with open(path, "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "except urllib.error.HTTPError as e:" in line:
        indent = len(line) - len(line.lstrip())
        ind_str = " " * indent
        new_lines.append(f"{ind_str}except urllib.error.HTTPError as e:\n")
        new_lines.append(f"{ind_str}    if e.code == 403:\n")
        new_lines.append(f'{ind_str}        print(json.dumps({{"status": "RATE_LIMITED", "detail": "Search API quota window active (403). Waiting for next cycle."}}))\n')
        new_lines.append(f"{ind_str}    else:\n")
        new_lines.append(f'{ind_str}        print(json.dumps({{"status": "ERROR", "detail": str(e)}}))\n')
        skip = True
        continue
    if skip:
        if line.strip().startswith("except Exception") or (line.strip() and len(line) - len(line.lstrip()) <= indent):
            skip = False
            new_lines.append(line)
        continue
    new_lines.append(line)

with open(path, "w") as f:
    f.writelines(new_lines)

try:
    py_compile.compile(path, doraise=True)
    print("✅ Sintaxis e indentación de github_scout_agent.py corregidas y verificadas.")
except Exception as err:
    print(f"⚠️ Error de compilación: {err}")
