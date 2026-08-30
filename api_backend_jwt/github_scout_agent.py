#!/usr/bin/env python3
"""
CCiA GitHub Scout Agent v1.1.0
Búsqueda autónoma de repositorios, leads y bounties en GitHub API.
Manejo gracioso de límites de tasa HTTP 403 / 429.
"""

import os
import sys
import json
import sqlite3
import urllib.request
import urllib.error

DB_PATH = "/home/k1/ccia_workspace/university.db"

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
        
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ccia_credentials';")
            if cur.fetchone():
                cur.execute("SELECT secret_key, value FROM ccia_credentials WHERE service_name = 'GITHUB_TOKEN' AND status = 'ACTIVE';")
                row = cur.fetchone()
                if row:
                    token = row[0] or row[1]
            if not token:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credentials';")
                if cur.fetchone():
                    cur.execute("SELECT secret FROM credentials WHERE service = 'GITHUB_TOKEN';")
                    row = cur.fetchone()
                    if row and row[0]:
                        token = row[0]
            conn.close()
        except Exception:
            pass
    return token

def run_scout():
    token = get_github_token()
    if token:
        prefix = token[:12] if len(token) >= 12 else token[:4]
        print(f"🔑 Usando GITHUB_TOKEN activo desde el Vault (Prefijo: {prefix}...).")
    else:
        print("ℹ️ GITHUB_TOKEN no configurado en Vault. Usando API pública de GitHub.")

    url = "https://api.github.com/search/repositories?q=help-wanted+language:python&sort=updated&order=desc&per_page=5"
    headers = {
        "User-Agent": "CCiA-Scout-Agent/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            total_count = data.get("total_count", 0)
            items = data.get("items", [])
            leads_found = len(items)
            print(json.dumps({
                "status": "SUCCESS",
                "total_count": total_count,
                "leads_found": leads_found,
                "detail": f"Scouted {leads_found} repository leads."
            }))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(json.dumps({
                "status": "RATE_LIMITED",
                "detail": "Search API quota window active (403). Waiting for next cycle."
            }))
        else:
            print(json.dumps({"status": "ERROR", "detail": f"HTTP Error {e.code}"}))
    except Exception as e:
        print(json.dumps({"status": "ERROR", "detail": str(e)}))

if __name__ == "__main__":
    run_scout()
