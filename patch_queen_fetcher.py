import os
import re

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Módulo de descarga de contexto para la Reina
    fetcher_code = '''
import urllib.request
import json
import re

def fetch_bounty_context(repo_issue: str) -> str:
    """Obtiene el contenido real del issue de GitHub para inyectarlo a la Reina"""
    try:
        if "#" in repo_issue:
            repo, issue_num = repo_issue.split("#")
            url = f"https://api.github.com/repos/{repo}/issues/{issue_num}"
            req = urllib.request.Request(url, headers={'User-Agent': 'CCIA-Swarm'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                title = data.get('title', '')
                body = data.get('body', '')
                return f"TÍTULO DEL ISSUE: {title}\\nCUERPO DEL ISSUE:\\n{body}"
    except Exception as e:
        return f"Contexto local del issue: {repo_issue} (No se pudo conectar a GitHub API: {e})"
    return f"Contexto de la tarea: {repo_issue}"

def clean_r1_output(text: str) -> str:
    """Limpia las trazas de pensamiento <think> de DeepSeek-R1"""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()
'''

    if "def fetch_bounty_context" not in content:
        content = fetcher_code + "\n" + content
        
        # Parchear la llamada de la Reina Q1 para inyectar contexto descargado
        old_q1_call = "q1_prompt = "
        if old_q1_call in content:
            content = content.replace(
                old_q1_call,
                "bounty_ctx = fetch_bounty_context(target_bounty)\n        q1_prompt = f'{bounty_ctx}\\n\\n' + "
            )

        with open(mando_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Parche cargado: La Reina ahora descarga el contenido de GitHub antes de evaluar.")
    else:
        print("ℹ️ El extractor HTTP ya está instalado en ccia_mando_63.py.")
