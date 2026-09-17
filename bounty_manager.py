#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_bounties(status=None, limit=None, order_by_reward=True):
    """Consulta todos los bounties filtrando spam automáticamente sin restricción de 20."""
    conn = get_db()
    query = "SELECT * FROM bounty_opportunities WHERE repo NOT LIKE '%bounty-plaza%'"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if order_by_reward:
        query += " ORDER BY reward DESC, id DESC"
    else:
        query += " ORDER BY id DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor = conn.cursor()
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_bounty(repo, issue_id, title, reward=0.0, issue_url=None, status="PENDING"):
    """Ingesta limpia: ignora automáticamente los repositorios o títulos con spam."""
    if "bounty-plaza" in str(repo) or "999999999" in str(title):
        return False

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bounty_opportunities (repo, issue_id, title, reward, issue_url, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(issue_url) DO UPDATE SET
            reward=excluded.reward,
            title=excluded.title,
            status=excluded.status
    """, (repo, str(issue_id), title, float(reward) if reward else 0.0, issue_url, status))
    conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    bounties = get_bounties()
    print(f"✅ [Paso 2] Módulo Activo. Bounties reales disponibles en DB: {len(bounties)}")
