import re
import os

smart_search_code = '''
    def search_real_bounties(self, query="bounty", min_stars=5, limit=10):
        """Buscador Inteligente de Bounties reales con filtros flexibilizados."""
        import subprocess, json
        
        blacklisted_terms = ["bounty-plaza", "omniblocks", "seed a paid"]
        
        # Búsqueda estructurada por etiquetas de recompensa/trabajo comunitario
        gh_cmd = [
            "gh", "search", "issues",
            query,
            "--state=open",
            f"--qualifier=stars:>{min_stars}",
            f"--limit={limit * 3}",
            "--json", "repository,number,title,body,labels,url"
        ]
        
        try:
            res = subprocess.run(gh_cmd, capture_output=True, text=True, timeout=20)
            data = json.loads(res.stdout) if res.stdout.strip() else []
            
            # Fallback si no hay resultados directos: buscar por etiqueta "bounty"
            if not data:
                gh_cmd[3] = "label:bounty,algora,polar"
                res = subprocess.run(gh_cmd, capture_output=True, text=True, timeout=20)
                data = json.loads(res.stdout) if res.stdout.strip() else []

            filtered_results = []
            for item in data:
                repo_full = item.get("repository", {}).get("nameWithOwner", "")
                title = item.get("title", "")
                
                is_spam = any(term in repo_full.lower() or term in title.lower() for term in blacklisted_terms)
                if not is_spam and repo_full:
                    filtered_results.append({
                        "repo": repo_full,
                        "number": item.get("number"),
                        "title": title,
                        "body": item.get("body", ""),
                        "url": item.get("url", f"https://github.com/{repo_full}/issues/{item.get('number')}")
                    })
                if len(filtered_results) >= limit:
                    break
                    
            return filtered_results
        except Exception as e:
            print(f"⚠️ Error en Buscador Inteligente: {e}")
            return []
'''

target_files = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for filepath in target_files:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Reemplazar implementación previa de search_real_bounties
        if "def search_real_bounties" in content:
            pattern = r"def search_real_bounties\(.*?\):\n(?:[ \t]+.*?\n)+"
            content = re.sub(pattern, smart_search_code.strip() + "\n", content)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Buscador actualizado en: {filepath}")

