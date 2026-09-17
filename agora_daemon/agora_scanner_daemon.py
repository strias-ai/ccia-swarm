import os
import time
import subprocess
import json
import re
import sqlite3
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"
LOG_FILE = os.path.expanduser("~/ccia_workspace/agora_daemon/scanner.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def analyze_value(title, body="", stars=0):
    text = f"{title} {body}"
    
    usd_match = re.search(r'\$\s?(\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    jpy_match = re.search(r'(\d+)\s?(?:JPY|¥|yens)', text, re.IGNORECASE)
    eur_match = re.search(r'€\s?(\d+)|(\d+)\s?EUR', text, re.IGNORECASE)
    crypto_match = re.search(r'(\d+(?:\.\d+)?)\s?(USDC|SOL|ETH|BTC|USDT)', text, re.IGNORECASE)
    points_match = re.search(r'(\d+)\s?(?:pts|points|puntos)', text, re.IGNORECASE)

    raw_reward = "Sin especificar"
    value_type = "REPUTACION"
    amount_usd_equiv = 0.0
    
    if usd_match:
        amount_usd_equiv = float(usd_match.group(1))
        raw_reward = f"${amount_usd_equiv:.2f} USD"
        value_type = "FIAT"
    elif crypto_match:
        val, token = crypto_match.groups()
        raw_reward = f"{val} {token.upper()}"
        value_type = "CRYPTO"
        amount_usd_equiv = float(val) if token.upper() in ["USDC", "USDT"] else float(val) * 150.0
    elif jpy_match:
        jpy_val = float(jpy_match.group(1))
        raw_reward = f"{jpy_val:.0f} JPY"
        value_type = "POINTS_FIAT"
        amount_usd_equiv = jpy_val / 155.0
    elif points_match:
        pts = points_match.group(1)
        raw_reward = f"{pts} PTS"
        value_type = "PUNTOS"
        amount_usd_equiv = float(pts) * 0.1
        
    rep_score = min(100.0, float(stars) * 1.5 + (20.0 if value_type != "REPUTACION" else 5.0))
    
    val_json = json.dumps({
        "raw": raw_reward,
        "type": value_type,
        "usd_equivalent": round(amount_usd_equiv, 2),
        "reputation_score": round(rep_score, 1)
    })
    
    return value_type, raw_reward, round(amount_usd_equiv, 2), round(rep_score, 1), val_json

def record_bounty(repo, issue_num, title, url, body="", stars=0):
    try:
        v_type, raw_rew, usd_amt, rep_score, val_json = analyze_value(title, body, stars)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM bounty_opportunities WHERE repo = ? AND issue_number = ?", (repo, issue_num))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                INSERT INTO bounty_opportunities 
                (repo, issue_number, title, bounty_amount, status, url, value_type, raw_reward, reputation_score, value_json)
                VALUES (?, ?, ?, ?, 'DISCOVERED', ?, ?, ?, ?, ?)
            """, (repo, issue_num, title, usd_amt, url, v_type, raw_rew, rep_score, val_json))
            conn.commit()
            log(f"💾 [VALOR: {raw_rew} | REP: {rep_score}] Registrada: {repo}#{issue_num}")
        else:
            cursor.execute("""
                UPDATE bounty_opportunities 
                SET value_type = ?, raw_reward = ?, reputation_score = ?, value_json = ?, bounty_amount = ?
                WHERE id = ?
            """, (v_type, raw_rew, rep_score, val_json, usd_amt, row[0]))
            conn.commit()
            log(f"🔄 [ACTUALIZADO: {raw_rew}] Repositorio {repo}#{issue_num}")
            
        conn.close()
    except Exception as e:
        log(f"⚠️ Error al escribir en DB: {e}")

def scan_bounties():
    log("🔍 Escaneo Profundo y Paginado (Opire, Algora, Boss)...")
    queries = [
        'opire state:open',
        'algora state:open',
        'bounty state:open stars:>10'
    ]
    
    blacklist = ["bounty-plaza", "BountyScout", "ClaudeEarnSelf"]
    total_found = 0

    for q in queries:
        cmd = ['gh', 'search', 'issues', q, '--limit', '50', '--json', 'number,title,url,repository,body,stargazersCount']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            try:
                items = json.loads(res.stdout)
                for item in items:
                    repo = item.get("repository", {}).get("nameWithOwner", "desconocido")
                    stars = item.get("repository", {}).get("stargazersCount", 0)
                    num = item.get("number")
                    title = item.get("title", "")
                    url = item.get("url", "")
                    body = item.get("body", "")
                    
                    if any(spam in repo for spam in blacklist):
                        continue
                        
                    record_bounty(repo, num, title, url, body, stars)
                    total_found += 1
            except Exception as e:
                log(f"⚠️ Error procesando JSON: {e}")
                
    log(f"🏁 Escaneo profundo completado. Oportunidades analizadas: {total_found}")

if __name__ == '__main__':
    log("🚀 Daemon Ágora con Evaluador Holístico de Valor Iniciado.")
    while True:
        try:
            scan_bounties()
        except Exception as e:
            log(f"⚠️ Error en bucle: {e}")
        time.sleep(900)
