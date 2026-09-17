#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import subprocess
import json
import re

DB_PATH = '/home/k1/ccia_workspace/university.db'

def get_repo_stars(repo):
    if not repo or '/' not in repo:
        return 0
    try:
        cmd = ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip().isdigit():
            return int(res.stdout.strip())
    except Exception:
        pass
    return 0

def extract_reward(text):
    if not text:
        return 0.0
    # Buscar patrones como $500, $1,500, $10000, 500 USD, etc.
    matches = re.findall(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', text)
    if matches:
        try:
            return max([float(m.replace(',', '')) for m in matches])
        except Exception:
            pass
    return 0.0

def main():
    print("=========================================================================")
    print("🌟 TOP 10 BOUNTIES CON MÁS ESTRELLAS ⭐ Y MEJOR RECOMPENSA 💰")
    print("=========================================================================\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Seleccionar issues pendientes excluyendo meta-bots de alertas
    c.execute("""
        SELECT * FROM bounty_opportunities 
        WHERE status IN ('PENDING', 'SUBMITTED') 
          AND repo NOT LIKE '%BountyScout%' 
          AND title NOT LIKE '%Bounty Alert%' 
          AND title NOT LIKE '%[radar]%'
        LIMIT 100
    """)
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("⚠️ No se encontraron bounties válidos en la base de datos.")
        return

    print(f"🔍 Evaluando {len(rows)} proyectos reales en GitHub...\n")

    enriched = []
    repo_stars_cache = {}

    for r in rows:
        d = dict(r)
        repo = d.get('repo', '')
        title = d.get('title', '')
        body = d.get('issue_body', '') or ''
        
        # Calcular/Extraer recompensa
        reward = extract_reward(title) or extract_reward(body)
        
        # Consultar estrellas del repo (usando caché para no saturar la API)
        if repo not in repo_stars_cache:
            repo_stars_cache[repo] = get_repo_stars(repo)
        stars = repo_stars_cache[repo]

        enriched.append({
            'id': d.get('id'),
            'repo': repo,
            'title': title,
            'url': d.get('issue_url'),
            'reward': reward,
            'stars': stars,
            'status': d.get('status')
        })

    # Ordenar priorizando por número de estrellas y luego por recompensa
    enriched.sort(key=lambda x: (x['stars'], x['reward']), reverse=True)

    top10 = enriched[:10]

    for idx, item in enumerate(top10, 1):
        reward_str = f"${item['reward']:,.2f} USD" if item['reward'] > 0 else "Recompensa en repo / Por definir"
        print(f"🏆 #{idx} | ⭐ Estrellas: {item['stars']:<6} | 💰 Recompensa: {reward_str}")
        print(f"   📦 Repositorio: {item['repo']}")
        print(f"   📌 Título:      {item['title']}")
        print(f"   🔗 URL:         {item['url']}")
        print(f"   🚥 Estado DB:   {item['status']}")
        print("   " + "-" * 67)

if __name__ == '__main__':
    main()
