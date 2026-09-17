#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCIA2 - Demonio Autónomo Art.63 (Versión Definitiva Enterprise)
Sincronización completa: Ingesta de Issue -> Generación Multicapa LLM -> Publicación GH -> Registro DB
"""

import time
import datetime
import urllib.request
import json
import subprocess
import sqlite3
import sys
from bounty_manager import get_bounties, get_db

DB_PATH = '/home/k1/ccia_workspace/university.db'
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"
POLL_INTERVAL_EMPTY = 10
WORK_INTERVAL = 4

def log(msg, level="INFO"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [{level}] [ART63-DAEMON] {msg}", flush=True)

def ensure_db_schema():
    """Garantiza la existencia de las columnas necesarias en la DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for col in [("issue_body", "TEXT"), ("generated_response", "TEXT")]:
        try:
            c.execute(f"ALTER TABLE bounty_opportunities ADD COLUMN {col[0]} {col[1]};")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

class GitHubService:
    @staticmethod
    def fetch_issue_body(url):
        try:
            cmd = ["gh", "issue", "view", url, "--json", "body"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout).get("body", "")
        except Exception as e:
            log(f"Error al obtener cuerpo de issue en {url}: {e}", level="WARN")
        return ""

    @staticmethod
    def publish_comment(url, content):
        if not url:
            return False
        try:
            cmd = ["gh", "issue", "comment", url, "--body", content]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            return res.returncode == 0
        except Exception as e:
            log(f"Error al publicar comentario en {url}: {e}", level="ERROR")
            return False

class LLMEngine:
    @classmethod
    def generate_solution(cls, repo, title, body):
        prompt = f"""You are a Senior Principal Engineer solving a bounty issue for '{repo}'.

ISSUE TITLE: {title}

ISSUE DESCRIPTION:
{body[:3500]}

INSTRUCTIONS:
1. Provide an Executive Summary & Root Cause Analysis.
2. Provide full, ready-to-use CODE FIXES for ALL affected files (both Backend and Frontend if applicable).
3. Do NOT omit code or use placeholder comments like '// rest of code here'.
4. Provide a Testing & Verification strategy.

Format your output in clean Markdown.
"""
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": 4096}
        }).encode('utf-8')

        req = urllib.request.Request(OLLAMA_URL, data=payload, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                response_text = data.get("response", "").strip()
                return response_text if len(response_text) > 150 else None
        except Exception as e:
            log(f"Error invocando Ollama: {e}", level="ERROR")
            return None

class BountyWorker:
    @staticmethod
    def is_bot_issue(title, repo):
        bot_patterns = ["Bounty Alert", "[radar]", "New Opportunityies found"]
        return any(p in title for p in bot_patterns) or "BountyScout" in repo

    @classmethod
    def process_pending(cls):
        # Priorizar por recompensa económica (order_by_reward=True)
        pending = get_bounties(status='PENDING', limit=1, order_by_reward=True)
        if not pending:
            return False

        item = pending[0]
        b_id, repo, title, url = item['id'], item.get('repo', ''), item.get('title', ''), item.get('issue_url', '')

        if cls.is_bot_issue(title, repo):
            conn = get_db()
            c = conn.cursor()
            c.execute("UPDATE bounty_opportunities SET status='SKIPPED' WHERE id=?", (b_id,))
            conn.commit()
            conn.close()
            log(f"⏭️ Omitida alerta de bot ID #{b_id} [{repo}]")
            return True

        log(f"⚡ Procesando Bounty ID #{b_id} | [{repo}] {title[:45]}...")

        body = GitHubService.fetch_issue_body(url) if url else title
        solution = LLMEngine.generate_solution(repo, title, body if body else title)

        if not solution:
            log(f"⚠️ Reintentando ID #{b_id} en siguiente ciclo por fallo de LLM.", level="WARN")
            return False

        # Publicación real en GitHub antes de marcar SUBMITTED
        published = GitHubService.publish_comment(url, solution)
        final_status = 'SUBMITTED' if published else 'GENERATED'

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            UPDATE bounty_opportunities 
            SET status=?, issue_body=?, generated_response=? 
            WHERE id=?
        """, (final_status, body, solution, b_id))
        conn.commit()
        conn.close()

        log(f"✅ Bounty ID #{b_id} procesado. Estado DB: {final_status} | Enviado a GitHub: {published}")
        return True

def main():
    ensure_db_schema()
    log("🚀 Demonio Autónomo Art.63 Operativo (Ollama + GitHub CLI + Recompensas Prioritarias)...")
    while True:
        try:
            has_work = BountyWorker.process_pending()
            time.sleep(WORK_INTERVAL if has_work else POLL_INTERVAL_EMPTY)
        except KeyboardInterrupt:
            log("🛑 Demonio detenido manualmente.")
            sys.exit(0)
        except Exception as e:
            log(f"⚠️ Excepción general: {e}", level="ERROR")
            time.sleep(5)

if __name__ == '__main__':
    main()
