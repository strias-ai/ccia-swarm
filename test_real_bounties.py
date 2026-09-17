import json
import subprocess

print("\n" + "="*80)
print("🛸 CCIA EXPLORADOR DE BOUNTIES REALES (Algora, Opire, Boss, Recompensas en vivo)")
print("="*80)

# Patrones exactos usados por las plataformas de bounties en GitHub
patterns = [
    ('Algora Bounties', '"/bounty $" in:body state:open type:issue'),
    ('Opire Rewards', '"/reward" in:body state:open type:issue'),
    ('Boss Bounties', '"/boss $" in:body state:open type:issue'),
    ('Rust Bounties', '"bounty" language:rust state:open type:issue'),
    ('Go Bounties', '"bounty" language:go state:open type:issue')
]

for label, query in patterns:
    print(f"\n🔍 Buscando {label} -> Query: [{query}]")
    cmd = ['gh', 'search', 'issues', query, '--limit', '5', '--json', 'number,title,url,repository,body']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        try:
            items = json.loads(res.stdout)
            if not items:
                print("   ℹ️ Sin resultados activos en esta categoría.")
            else:
                print(f"   🎯 ¡Encontradas {len(items)} oportunidades!")
                for item in items:
                    repo = item.get("repository", {}).get("nameWithOwner", "desconocido")
                    title = item.get("title", "")[:60]
                    url = item.get("url", "")
                    print(f"     • [{repo}#{item.get('number')}] {title}")
                    print(f"       🔗 {url}")
        except Exception as e:
            print(f"   ⚠️ Error parseando JSON: {e}")
    else:
        print(f"   ⚠️ CLI Error: {res.stderr.strip()}")

print("="*80 + "\n")
