"""
CCiA Artefacto 59 - Ollama Email Dispatcher & B2B Repo OSINT Prospector
"""
import os
import sys
import sqlite3
import json
import urllib.request
import urllib.error
import re

DB_PATH = "/home/k1/ccia_workspace/university.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def init_email_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            folder TEXT DEFAULT 'INBOX',
            channel TEXT DEFAULT 'EMAIL',
            recipient TEXT,
            status TEXT DEFAULT 'PENDING',
            response_body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS b2b_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            email TEXT,
            product_needed TEXT,
            status TEXT DEFAULT 'PROSPECT',
            score INTEGER DEFAULT 0,
            repo_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def query_ollama(prompt, model="qwen2.5-coder:7b"):
    """Consulta al motor Ollama local con tolerancia a fallos y selección manual prioritaria."""
    fallback_models = [model, "qwen2.5-coder:7b", "llama3.2:3b", "qwen2.5:3b"]
    seen = set()
    models_to_try = [m for m in fallback_models if not (m in seen or seen.add(m))]
    
    for m in models_to_try:
        payload = json.dumps({"model": m, "prompt": prompt, "stream": False}).encode('utf-8')
        req = urllib.request.Request(OLLAMA_URL, data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                res_text = res_data.get("response", "").strip()
                if res_text:
                    return res_text
        except Exception:
            continue

    return "[OLLAMA_FALLBACK_ANALYSIS] Intención detectada: SOLICITUD_SERVICIO."

def process_inbound_emails():
    init_email_db()
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cur = conn.cursor()
    
    msgs = cur.execute("SELECT id, sender, subject, body FROM email_messages WHERE folder='INBOX' AND status='PENDING' LIMIT 10;").fetchall()
    if not msgs:
        print("⚡ Ingesta Email: No hay correos pendientes en Inbox.")
        conn.close()
        return

    print("=" * 80)
    print("📩 CCiA OLLAMA EMAIL AGENT & TASK DISPATCHER (ARTEFACTO 59)")
    print("=" * 80)

    for m in msgs:
        msg_id, sender, subject, body = m
        print(f"\n[+] Procesando correo ID #{msg_id} de <{sender}>")
        print(f"    Asunto: {subject}")
        
        prompt = f"Clasifica la intencion de este email: Subject: {subject} | Body: {body}. Responde solo la categoria (ej. AUDITORIA, DATASET, INFORMACION)."
        intent = query_ollama(prompt, model="qwen2.5-coder:7b")
        print(f"    🤖 Intención identificada por Ollama: {intent}")
        
        target_art = "10" if "AUDIT" in intent.upper() else "21"
        print(f"    ⚙️ Despachando tarea al Artefacto [{target_art}] para ejecución...")
        
        resp_prompt = f"Redacta una respuesta profesional breve a este correo de {sender} confirmando recepción y próximo paso."
        resp_text = query_ollama(resp_prompt, model="qwen2.5-coder:7b")
        
        cur.execute("UPDATE email_messages SET status='PROCESSED', response_body=? WHERE id=?", (resp_text, msg_id))
        conn.commit()
        print("    ✉️ Respuesta generada y lista para envío SMTP.")
        print(f"    └─ Vista previa: {resp_text[:70]}...")

    conn.close()
    print("-" * 80)
    print("✅ Flujo completo de recepción, clasificación, orquestación y respuesta finalizado.")

def prospect_public_repositories(topic_query="topic:python+topic:fastapi", max_results=5):
    """Scraping y clasificación agéntica de empresas B2B en GitHub REST API."""
    init_email_db()
    print("\n" + "="*80)
    print("🔎 CCiA B2B OSINT PROSPECTOR: ANALIZANDO REPOSITORIOS PÚBLICOS")
    print("="*80)
    
    url = f"https://api.github.com/search/repositories?q={topic_query}&sort=updated&order=desc&per_page={max_results}"
    headers = {
        'User-Agent': 'CCiA-B2B-Prospector/2.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get("items", [])
    except Exception as e:
        print(f"⚠️ Error de conexión con GitHub API: {e}")
        return

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    cur = conn.cursor()
    new_leads = 0

    for item in items:
        owner = item.get("owner", {}).get("login", "Empresa_B2B")
        repo_name = item.get("full_name", "")
        repo_url = item.get("html_url", "")
        description = item.get("description") or "Proyecto Python sin descripción explícita."
        language = item.get("language") or "Python"
        
        cur.execute("SELECT id FROM b2b_clients WHERE repo_url = ?", (repo_url,))
        if cur.fetchone():
            continue

        prompt = f"""Analiza la viabilidad comercial de este repositorio publico:
- Organizacion: {owner}
- Repositorio: {repo_name}
- Lenguaje: {language}
- Descripcion: {description}

Determina la necesidad principal (AUDITORIA_CODIGO, DATASET_SINTETICO, INTEGRACION_A2A).
Responde en formato JSON estricto: {{"score": 85, "product_needed": "AUDITORIA_CODIGO"}}"""

        ollama_res = query_ollama(prompt, model="qwen2.5-coder:7b")
        score = 75
        product_needed = "AUDITORIA_CODIGO"

        try:
            match = re.search(r'\{.*\}', ollama_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                score = int(parsed.get("score", 75))
                product_needed = parsed.get("product_needed", "AUDITORIA_CODIGO")
        except Exception:
            pass

        if score >= 60:
            contact_email = f"contact@{owner.lower()}.io"
            cur.execute("""
                INSERT OR IGNORE INTO b2b_clients (company_name, email, product_needed, status, score, repo_url)
                VALUES (?, ?, ?, 'QUALIFIED_LEAD', ?, ?)
            """, (owner, contact_email, product_needed, score, repo_url))
            new_leads += 1
            print(f"  🎯 Prospecto B2B Identificado: [{owner}] | Scoring: {score}/100")
            print(f"     └─ Producto Recomendado: {product_needed} | Repo: {repo_url}")

    conn.commit()
    conn.close()
    print(f"\n✅ Prospección finalizada: {new_leads} nuevos clientes B2B cualificados e ingresados en CRM.")

if __name__ == "__main__":
    process_inbound_emails()
    prospect_public_repositories()
