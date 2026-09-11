import os
import re

print("================================================================================")
print("🚀 INSTALANDO BUSCADOR INTELIGENTE DE BOUNTIES REALES (PRODUCTION GRADE)")
print("================================================================================")

smart_search_code = '''
    def search_real_bounties(self, query="bounty", min_stars=20, limit=15):
        """Buscador Inteligente de Bounties con filtro de reputación y exclusión de spam."""
        import subprocess, json
        
        # Palabras/Usuarios excluidos (granjas de spam conocidas)
        blacklisted_terms = ["bounty-plaza", "omniblocks", "seed a paid"]
        
        # Filtro avanzado para GitHub CLI
        gh_cmd = [
            "gh", "search", "issues",
            f"{query}",
            "--state=open",
            f"--qualifier=stars:>{min_stars}",
            f"--limit={limit * 2}",
            "--json", "repository,number,title,body,labels,updatedAt"
        ]
        
        try:
            res = subprocess.run(gh_cmd, capture_output=True, text=True, timeout=20)
            if res.returncode != 0 or not res.stdout.strip():
                # Fallback con búsqueda por etiqueta si la búsqueda de texto da pocos resultados
                gh_cmd[3] = f'label:"bounty" {query}'
                res = subprocess.run(gh_cmd, capture_output=True, text=True, timeout=20)
            
            data = json.loads(res.stdout) if res.stdout.strip() else []
            filtered_results = []
            
            for item in data:
                repo_full = item.get("repository", {}).get("nameWithOwner", "")
                title = item.get("title", "")
                
                # Check Blacklist
                is_spam = any(term in repo_full.lower() or term in title.lower() for term in blacklisted_terms)
                if not is_spam and repo_full:
                    filtered_results.append({
                        "repo": repo_full,
                        "number": item.get("number"),
                        "title": title,
                        "body": item.get("body", ""),
                        "url": f"https://github.com/{repo_full}/issues/{item.get('number')}"
                    })
                if len(filtered_results) >= limit:
                    break
                    
            return filtered_results
        except Exception as e:
            print(f"⚠️ Error en Buscador Inteligente: {e}")
            return []
'''

files_to_patch = [
    "/home/k1/ccia_workspace/modules/art_63.py",
    "/home/k1/ccia_workspace/ccia_mando_63.py"
]

for filepath in files_to_patch:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "def search_real_bounties" not in content:
            # Inyectar el método dentro de la clase principal
            class_match = re.search(r"class (TriSwarmOrchestrator|CCiAMando63)[^:]*:", content)
            if class_match:
                insert_pos = class_match.end()
                content = content[:insert_pos] + "\n" + smart_search_code + content[insert_pos:]
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Buscador Inteligente inyectado en: {filepath}")
        else:
            print(f"ℹ️ El Buscador Inteligente ya estaba presente en: {filepath}")

print("================================================================================")
print("✨ BUSCADOR DE BOUNTIES DE PRODUCCIÓN CONFIGURADO")
print("================================================================================")
