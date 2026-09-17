import os
import json
import subprocess
import urllib.request
import urllib.error

ISSUEHUNT_KEY = os.getenv("ISSUEHUNT_API_KEY", "api_27710be0855bff9b2fd7d0bbf1e49bac6d45bbd7cbe1d60aefcec5b0df204979")

print("\n" + "="*80)
print("🛸 CCIA EXPLORADOR DE FUENTES DE BOUNTIES (ÁGORA / GITHUB vs ISSUEHUNT)")
print("="*80)

# 1. BÚSQUEDA GITHUB CLI
print("\n[1] 🔍 Pruebas en GitHub / Ágora (Bounties con GitHub CLI):")
queries = [
    'label:bounty state:open language:rust',
    'label:bounty state:open language:go',
    'label:bounty state:open'
]

for q in queries:
    print(f"\n  👉 Búsqueda: '{q}'")
    # Usamos jq/fields validos para evitar 'Unknown JSON field'
    cmd = ['gh', 'search', 'issues', q, '--limit', '3', '--json', 'number,title,url,repository']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        try:
            items = json.loads(res.stdout)
            if not items:
                print("     ℹ️ Sin resultados.")
            for item in items:
                repo_name = item.get("repository", {}).get("nameWithOwner", "desconocido")
                print(f"     • [{repo_name}#{item.get('number')}] {item.get('title')[:60]}...")
                print(f"       🔗 {item.get('url')}")
        except Exception as e:
            print(f"     ⚠️ Error parseando JSON: {e}")
    else:
        print(f"     ⚠️ Error ejecutando gh search: {res.stderr.strip()}")

# 2. BÚSQUEDA ISSUEHUNT GRAPHQL API
print("\n" + "-"*80)
print(f"[2] 🎯 Pruebas con IssueHunt GraphQL / API Key:")

graphql_url = "https://api.issuehunt.io/graphql"
gql_query = {
    "query": """
    query {
      issues(first: 3) {
        nodes {
          id
          title
          url
          bountyAmount
        }
      }
    }
    """
}

headers = {
    "Authorization": f"Bearer {ISSUEHUNT_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "CCIA-MissionControl/19.0"
}

data_bytes = json.dumps(gql_query).encode('utf-8')
req = urllib.request.Request(graphql_url, data=data_bytes, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        body = response.read().decode('utf-8')
        print("  ✅ Respuesta GraphQL recibida:")
        print(f"     {body[:300]}...\n")
except urllib.error.HTTPError as e:
    print(f"  ⚠️ Error HTTP GraphQL {e.code}: {e.reason}")
    body = e.read().decode('utf-8')
    print(f"  📄 Detalle: {body[:200]}")
    
    # Intento Fallback REST API
    print("\n  🔄 Probando Fallback REST (https://issuehunt.io/api/v1/issues)...")
    rest_url = "https://issuehunt.io/api/v1/issues"
    req_rest = urllib.request.Request(rest_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req_rest, timeout=10) as resp2:
            print(f"  ✅ Fallback REST exitoso (HTTP {resp2.getcode()}):")
            print(f"     {resp2.read().decode('utf-8')[:300]}...")
    except Exception as ex:
        print(f"  ❌ Error Fallback REST: {ex}")
except Exception as e:
    print(f"  ❌ Error de conexión: {e}")

print("="*80 + "\n")
