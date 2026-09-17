#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import time
import os
from bounty_manager import get_db

def render_cascada():
    os.system('clear')
    conn = get_db()
    c = conn.cursor()

    # Resumen de métricas
    c.execute("SELECT status, COUNT(*) FROM bounty_opportunities GROUP BY status")
    stats = dict(c.fetchall())

    print("=========================================================================")
    print("🌊 MONITOR EN CASCADA CCIA2 - RESOLUCIÓN DE BOUNTIES EN TIEMPO REAL")
    print("=========================================================================")
    print(f" 📊 PENDING: {stats.get('PENDING', 0)} | PROCESSING: {stats.get('PROCESSING', 0)} | SUBMITTED: {stats.get('SUBMITTED', 0)} | COMPLETED: {stats.get('COMPLETED', 0)}")
    print("-------------------------------------------------------------------------")
    print(f"{'ID':<6} | {'ESTADO':<10} | {'REPOSITORIO':<25} | {'TÍTULO DE LA ISSUE':<35}")
    print("-------------------------------------------------------------------------")

    # Últimos 15 registros procesados o en proceso (Vista en cascada)
    c.execute("""
        SELECT id, status, repo, title 
        FROM bounty_opportunities 
        WHERE status IN ('PROCESSING', 'SUBMITTED', 'COMPLETED', 'PENDING')
        ORDER BY id DESC LIMIT 15
    """)
    rows = c.fetchall()
    conn.close()

    for r in rows:
        b_id, st, repo, title = r['id'], r['status'], r['repo'] or 'N/A', r['title'] or 'N/A'
        
        # Color coding según estado
        icon = "⏳" if st == "PENDING" else "⚡" if st == "PROCESSING" else "✅" if st in ("SUBMITTED", "COMPLETED") else "❌"
        
        print(f"{b_id:<6} | {icon} {st:<8} | {repo[:25]:<25} | {title[:35]:<35}")

    print("=========================================================================")
    print("Presiona Ctrl+C para salir de la cascada.")

if __name__ == '__main__':
    try:
        while True:
            render_cascada()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n👋 Monitor en cascada cerrado.")
