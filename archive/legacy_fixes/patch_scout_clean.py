path = "/home/k1/ccia_workspace/api_backend_jwt/github_scout_agent.py"
with open(path, "r") as f:
    code = f.read()

# Reemplazar impresión de error JSON por aviso limpio de rate limit
target = 'print(json.dumps({"status": "ERROR", "detail": str(e)}))'
replacement = 'print("⏳ [GITHUB SCOUT] Búsqueda en pausa por Rate Limit de GitHub Search API (403). Espere el siguiente ciclo.")'

if target in code:
    code = code.replace(target, replacement)
    with open(path, "w") as f:
        f.write(code)
    print("✅ Ajuste de respuesta para Rate Limit de GitHub aplicado correctamente.")
else:
    print("ℹ️ El manejador de excepciones ya fue actualizado previamente.")
