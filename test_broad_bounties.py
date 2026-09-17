import os
import json
import subprocess
import urllib.request
import urllib.error

ISSUEHUNT_KEY = os.getenv("ISSUEHUNT_API_KEY", "api_27710be0855bff9b2fd7d0bbf1e49bac6d45bbd7cbe1d60aefcec5b0df204979")

print("\n" + "="*80)
print("🛸 CCIA EXPLORACIÓN AMPLIADA DE BOUNTIES (ÁGORA / GITHUB & ISSUEHUNT)")
print("="*80)

# 1. BÚSQUEDA EN GITHUB CON PATRONES REALES
print("\n[1] 🔍 Buscando Bounties en GitHub (Búsqueda por Recompensas y Tags):")
queries = [
    'bounty state:open language:rust',
    'bounty state:open language:go',
    'label:"help wanted" label:bounty state:open',
    'label:bounty "$"'
]

for q in queries:
    print(f"\n  👉 Búsqueda: '{q}'")
    cmd = ['gh', 'search', 'issues', q, '--limit', '3', '--json', 'number,title,url,repository']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        try:
            items = json.loads(res.stdout)
            if not items:
                print("     ℹ️ Sin resultados para este patrón.")
            for item in items:
                repo_name = item.get("repository", {}).get("nameWithOwner", "desconocido")
                print(f"     • [{repo_name}#{item.get('number')}] {item.get('title')[:65]}")
                print(f"       🔗 {item.get('url')}")
        except Exception as e:
            print(f"     ⚠️ Error JSON: {e}")
    else:
        print(f"     ⚠️ Error CLI: {res.stderr.strip()}")

# 2. CONSULTA DIRECTA API ISSUEHUNT
print("\n" + "-"*80)
print(f"[2] 🎯 Consultando API de IssueHunt (Autenticado):")

url = "https://issuehunt.io/api/issues?limit=5"
headers = {
    "Authorization": f"Bearer {ISSUEHUNT_KEY}",
    "Accept": "application/json",
    "User-Agent": "CCIA-Scanner/1.0"
}

req = urllib.request.Request(url, headers=headers, method="GET")

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        body = response.read().decode('utf-8')
        data = json.loads(body)
        print("  ✅ Respuesta JSON de IssueHunt recibida con éxito:")
        items = data.get("issues", []) if isinstance(data, dict) else data
        for idx, item in enumerate(items[:5], 1):
            print(f"     {idx}. {item.get('title', 'Sin título')} | Reward: ${item.get('bountyAmount', 0)}")
except Exception as e:
    print(f"  ℹ️ Prueba Endpoint JSON IssueHunt: {e}")

print("="*80 + "\n")
