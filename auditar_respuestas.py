#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from bounty_manager import get_db

def auditar():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT id, repo, issue_id, title, status, issue_url, issue_body, generated_response
        FROM bounty_opportunities 
        WHERE status = 'SUBMITTED' AND generated_response IS NOT NULL AND issue_body IS NOT NULL
        ORDER BY id DESC LIMIT 3
    """)
    rows = c.fetchall()
    conn.close()

    print("=========================================================================")
    print("🔍 AUDITORÍA DETALLADA: PETICIÓN ORIGINAL VS. RESPUESTA GENERADA")
    print("=========================================================================\n")

    if not rows:
        print("⏳ Procesando primera respuesta completa con la nueva versión...")
        return

    for r in rows:
        print(f"📌 ID #{r['id']} | [{r['repo']}] Issue #{r['issue_id']}")
        print(f"   URL: {r['issue_url']}")
        print(f"   Título: {r['title']}")
        print("\n   📥 PETICIÓN ORIGINAL DE LA ISSUE:")
        body_lines = (r['issue_body'] or 'Sin descripción').split('\n')
        for line in body_lines[:4]:
            print(f"      {line}")
        if len(body_lines) > 4:
            print("      [... cuerpo de issue truncado ...]")

        print("\n   🤖 RESPUESTA/SOLUCIÓN TÉCNICA GENERADA:")
        resp_lines = (r['generated_response'] or '').split('\n')
        for line in resp_lines[:10]:
            print(f"      {line}")
        if len(resp_lines) > 10:
            print("      [... respuesta LLM truncada ...]")
        print("\n" + "=" * 73)

if __name__ == '__main__':
    auditar()
