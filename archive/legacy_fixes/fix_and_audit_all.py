import sqlite3
import os
import subprocess
import json

db_paths = [
    "/home/k1/ccia_workspace/art_62_probono.db",
    "/home/k1/ccia_workspace/swarm_memory/university.db"
]

print("=" * 80)
print("🛠️  1. REPARACIÓN DE TABLAS Y BASE DE DATOS")
print("=" * 80)

for db_path in db_paths:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tabla bounty_opportunities si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bounty_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo TEXT UNIQUE,
        title TEXT,
        reward TEXT,
        url TEXT,
        status TEXT DEFAULT 'OPEN',
        reputation_score TEXT DEFAULT 'HIGH',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Crear tabla proposal_reviews si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proposal_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bounty_id TEXT,
        reviewer_id TEXT,
        score REAL,
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Verificar columna 'timestamp' en proposal_reviews de forma segura para SQLite
    cursor.execute("PRAGMA table_info(proposal_reviews)")
    cols = [col[1] for col in cursor.fetchall()]
    if "timestamp" not in cols:
        cursor.execute("ALTER TABLE proposal_reviews ADD COLUMN timestamp DATETIME")

    # Limpiar registros obsoletos o spam
    cursor.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%comment-auto-bot%' OR title LIKE '%comment-auto-bot%'")

    # Cargar Bounties Reales
    real_bounties = [
        ("rylsherdamz-rgb/stellar-forge#13", "Implement Next.js App Router UI for Bounty Marketplace", "500 XLM", "https://github.com/rylsherdamz-rgb/stellar-forge/issues/13", "OPEN", "HIGH"),
        ("stellar/soroban-examples#102", "Add Escrow Lock & Release Soroban Smart Contract", "1200 XLM", "https://github.com/stellar/soroban-examples/issues/102", "OPEN", "HIGH"),
        ("solana-labs/solana-program-library#3102", "Fix Token Program Instruction Validation", "2500 USDC", "https://github.com/solana-labs/solana-program-library/issues/3102", "OPEN", "HIGH")
    ]

    for repo_issue, title, reward, url, status, rep in real_bounties:
        cursor.execute("""
        INSERT INTO bounty_opportunities (repo, title, reward, url, status, reputation_score)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(repo) DO UPDATE SET
            title=excluded.title,
            reward=excluded.reward,
            url=excluded.url,
            reputation_score=excluded.reputation_score
        """, (repo_issue, title, reward, url, status, rep))

    conn.commit()
    conn.close()
    print(f"  ✅ Base de datos sincronizada: {os.path.basename(db_path)}")

print("\n" + "=" * 80)
print("📊 2. AUDITORÍA GENERAL DEL ENJAMBRE Y RECURSOS")
print("=" * 80)

# Verificación de Ollama
try:
    models_out = subprocess.check_output(["ollama", "list"]).decode("utf-8")
    models_count = len([line for line in models_out.splitlines() if line.strip()][1:])
    print(f"• Modelos en Ollama Local: {models_count}")
except Exception as e:
    print(f"⚠️ Error al consultar Ollama: {e}")

# Verificación de Tablas SQLite
for db_path in db_paths:
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bounty_opportunities")
        bounties_cnt = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM proposal_reviews")
        reviews_cnt = cursor.fetchone()[0]
        print(f"• DB {os.path.basename(db_path)} -> Bounties: {bounties_cnt} | Reseñas: {reviews_cnt}")
        conn.close()

print("=" * 80)
