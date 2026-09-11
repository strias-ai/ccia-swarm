from modules.art_63 import TriSwarmOrchestrator

orch = TriSwarmOrchestrator()
results = orch.search_real_bounties(query="python fix", min_stars=20, limit=5)

print("\n🎯 BOUNTIES / ISSUES REALES ENCONTRADOS EN GITHUB (>20★):")
for i, r in enumerate(results, 1):
    repo = r["repo"]
    num = r["number"]
    title = r["title"]
    print(f"  [{i}] {repo}#{num} ── {title}")
