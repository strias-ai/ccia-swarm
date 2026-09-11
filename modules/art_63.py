
def with_ollama_mutex(func):
    def wrapper(*args, **kwargs):
        lock_obj = acquire_ollama_mutex()
        try:
            return func(*args, **kwargs)
        finally:
            release_ollama_mutex(lock_obj)
    return wrapper


# --- CERROJO MUTEX GLOBAL DE OLLAMA CCIA ---
OLLAMA_LOCK_FILE = "/tmp/ccia_ollama_global.lock"

def acquire_ollama_mutex():
    try:
        f = open(OLLAMA_LOCK_FILE, "w")
        fcntl.flock(f, fcntl.LOCK_EX)
        return f
    except Exception:
        return None

def release_ollama_mutex(lock_file_obj):
    try:
        if lock_file_obj:
            fcntl.flock(lock_file_obj, fcntl.LOCK_UN)
            lock_file_obj.close()
    except Exception:
        pass
# --------------------------------------------
import fcntl

def build_repo_context(repo_dir):
    """Extrae el árbol de archivos y snippets clave del repo clonado."""
    if not repo_dir or not os.path.exists(repo_dir):
        return "No hay repositorio clonado disponible."
    
    context = []
    context.append("=== ESTRUCTURA DE ARCHIVOS DEL REPOSITORIO ===")
    file_count = 0
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo_dir)
            context.append(f"- {rel_path}")
            file_count += 1
            if file_count > 40:
                break
        if file_count > 40:
            break

    context.append("\n=== CONTENIDO DE ARCHIVOS CLAVE ===")
    key_files = ['README.md', 'main.py', 'package.json', 'Cargo.toml', 'requirements.txt', 'go.mod']
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if f in key_files or f.endswith(('.py', '.rs', '.go', '.js', '.sol')):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, repo_dir)
                try:
                    with open(full_p, 'r', encoding='utf-8', errors='ignore') as c_file:
                        content = c_file.read(1500) # Primeros 1500 caracteres
                        context.append(f"--- INICIO ARCHIVO: {rel_p} ---\n{content}\n--- FIN ARCHIVO ---")
                except Exception:
                    pass
                if len(context) > 10:
                    break
    return "\n".join(context)


import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import os
import sys
import re
import json
import shutil
import sqlite3
import urllib
import urllib.request
import urllib.parse
import subprocess

def get_repo_files_context(repo_dir: str) -> str:
    if not os.path.exists(repo_dir):
        return "Estructura no disponible."
    try:
        files_out = subprocess.check_output(
            ["git", "-C", repo_dir, "ls-files"], stderr=subprocess.DEVNULL
        ).decode("utf-8").splitlines()
        return "\n".join(files_out[:30]) if files_out else "Repositorio vacío o sin archivos git."
    except Exception:
        return "Error al listar archivos del repositorio."

class TriSwarmOrchestrator:
    def __init__(self, db_path="/home/k1/ccia_workspace/university.db"):
        self.db_path = db_path
        self.ollama_url = "http://localhost:11434/api/generate"
        self.work_dir = "/tmp/bounty_work"
        self.log_file_path = "/tmp/art63_reasoning.log"
        os.makedirs(self.work_dir, exist_ok=True)
        if not os.path.exists(self.log_file_path):
            open(self.log_file_path, "w").close()
            
        self.config_path = "/home/k1/ccia_workspace/swarm_config.json"
        self.wallets_path = "/home/k1/ccia_workspace/wallets.json"
        
        self.wallets = self._load_wallets()
        self.brains, self.queen_brains = self._load_swarm_config()
        
        self.fallback_model = "huihui_ai/qwen2.5-coder-abliterate:14b"
        self.available_models = self._get_installed_models()
        self._init_and_migrate_db()

    def _load_wallets(self):
        if os.path.exists(self.wallets_path):
            try:
                with open(self.wallets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "lightning": "vellichorlate475846@getalby.com",
            "evm": "0x6040f4D8BA36214222d34E176634670407a9bC56",
            "btc_segwit": "bc1q9x5u8j8w4e2k8m7l0p3n6q9r2s5t8v1w4x7y0z",
            "solana": "7xKXtg2CW87d97TXJSDpbD5jBk45E5nQ58a3",
            "monero": "488nn1B4C9yFz83R152x4z...",
            "tron_usdt": "T9xK7z4L2pQ8mN1v5R3s2t1v4w5x6y7z8"
        }

    def _load_swarm_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("brains", []), data.get("queens", [])
            except Exception:
                pass
        return [], []

    def save_swarm_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"brains": self.brains, "queens": self.queen_brains}, f, indent=2)

    def _init_and_migrate_db(self):
        """Migración automática de esquema SQLite para garantizar compatibilidad con columnas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            def ensure_columns(table_name, required_cols_sql, required_cols_dict):
                cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({required_cols_sql});")
                cur.execute(f"PRAGMA table_info({table_name});")
                existing_cols = [c[1] for c in cur.fetchall()]
                for col, col_type in required_cols_dict.items():
                    if col not in existing_cols:
                        try:
                            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type};")
                            print(f"  🛠️ Columna '{col}' agregada exitosamente a la tabla '{table_name}'.")
                        except Exception as e:
                            pass

            ensure_columns(
                "bounty_opportunities",
                "id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, title TEXT, reward TEXT, status TEXT DEFAULT 'PENDING', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                {"repo": "TEXT", "issue_id": "TEXT", "title": "TEXT", "reward": "TEXT", "status": "TEXT"}
            )

            ensure_columns(
                "swarm_debates",
                "id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, swarm_layer INTEGER, brain_code TEXT, role_name TEXT, response_text TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                {"repo": "TEXT", "issue_id": "TEXT", "swarm_layer": "INTEGER", "brain_code": "TEXT", "role_name": "TEXT", "response_text": "TEXT"}
            )

            ensure_columns(
                "proposal_reviews",
                "id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, reviewer_queen TEXT, score INTEGER, status TEXT, comments TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                {"repo": "TEXT", "issue_id": "TEXT", "reviewer_queen": "TEXT", "score": "INTEGER", "status": "TEXT", "comments": "TEXT"}
            )

            conn.commit()
            conn.close()
            print("  ✅ Migración de esquema DB de extremo a extremo completada.")
        except Exception as e:
            print(f"⚠️ Error en migración DB: {e}")

    def _get_installed_models(self):
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def _resolve_model(self, model_name):
        for am in self.available_models:
            if model_name in am or am in model_name:
                return am
        return self.fallback_model

    def call_ollama_stream(self, model_name, role_code_or_name, role_name_or_prompt=None, prompt=None):
        if prompt is None:
            role_code = "SWARM"
            role_name = str(role_code_or_name)
            prompt_text = str(role_name_or_prompt)
        else:
            role_code = str(role_code_or_name)
            role_name = str(role_name_or_prompt)
            prompt_text = str(prompt)

        target_model = self._resolve_model(model_name)
        header = f"\n🧠 [CEREBRO {role_code} - {role_name}] Modelo: {target_model}\n" + "─" * 70 + "\n"
        
        sys.stdout.write(header)
        sys.stdout.flush()

        with open(self.log_file_path, "a", encoding="utf-8") as log_f:
            log_f.write(header)
            log_f.flush()

        data = {
            "model": target_model,
            "prompt": f"[{role_code} - {role_name}]\n{prompt_text}",
            "stream": True,
            "keep_alive": "5m"
        }
        
        full_response = ""
        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response, open(self.log_file_path, "a", encoding="utf-8") as log_f:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        text_part = chunk.get("response", "")
                        full_response += text_part
                        sys.stdout.write(text_part)
                        sys.stdout.flush()
                        log_f.write(text_part)
                        log_f.flush()
            
            footer = "\n" + "─" * 70 + "\n"
            sys.stdout.write(footer)
            sys.stdout.flush()
            with open(self.log_file_path, "a", encoding="utf-8") as log_f:
                log_f.write(footer)
                log_f.flush()
        except Exception as e:
            err_msg = f"\n⚠️ Error en inferencia con {target_model}: {e}\n"
            sys.stdout.write(err_msg)
            sys.stdout.flush()
            full_response = f"[Respuesta predeterminada de fallback para {role_name}]"
            
        return full_response.strip()

    def call_ollama_direct(self, model_name, role_code_or_name, role_name_or_prompt=None, prompt=None):
        return self.call_ollama_stream(model_name, role_code_or_name, role_name_or_prompt, prompt)

    def clone_and_extract_context(self, repo, title=""):
        """Clona el repositorio e inspeciona archivos clave (README, código fuente) para dar contexto real a la IA"""
        clean_repo = repo.replace("https://github.com/", "").replace(".git", "").strip("/")
        target_path = os.path.join(self.work_dir, clean_repo.replace("/", "_"))
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        url = f"https://github.com/{clean_repo}.git"
        print(f"📥 [GIT] Clonando e inspeccionando código de: {url}")
        
        code_context = ""
        tree_files = []
        
        try:
            res = subprocess.run(["git", "clone", "--depth", "1", url, target_path], capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                for root, _, files in os.walk(target_path):
                    if ".git" in root or "node_modules" in root or "bin" in root or "obj" in root:
                        continue
                    for f in files:
                        rel = os.path.relpath(os.path.join(root, f), target_path)
                        tree_files.append(rel)
                
                # 1. Fragmento de README
                readme_content = ""
                for f in tree_files:
                    if f.lower().startswith("readme"):
                        rf_path = os.path.join(target_path, f)
                        try:
                            with open(rf_path, "r", encoding="utf-8", errors="ignore") as rf:
                                readme_content = rf.read(1500)
                        except Exception: pass
                        break

                # 2. Búsqueda de código fuente relevante según palabras clave del título
                keywords = [k.lower() for k in title.replace("[", "").replace("]", "").replace(":", "").split() if len(k) > 2]
                relevant_snippets = []
                
                for f in tree_files[:60]:
                    if any(f.endswith(ext) for ext in [".cs", ".py", ".js", ".ts", ".rs", ".go", ".cpp", ".h", ".json"]):
                        full_f = os.path.join(target_path, f)
                        try:
                            with open(full_f, "r", encoding="utf-8", errors="ignore") as sf:
                                content = sf.read(2500)
                                if any(kw in content.lower() or kw in f.lower() for kw in keywords) or len(relevant_snippets) < 2:
                                    relevant_snippets.append(f"--- ARCHIVO FUENTE: {f} ---\n{content[:1200]}")
                        except Exception: pass
                        if len(relevant_snippets) >= 4:
                            break

                code_context = f"📁 ESTRUCTURA DEL PROYECTO:\n" + "\n".join(tree_files[:15]) + "\n\n"
                if readme_content:
                    code_context += f"📄 DOCUMENTACIÓN README:\n{readme_content}\n\n"
                if relevant_snippets:
                    code_context += "💻 CÓDIGO FUENTE REAL EXTRAÍDO:\n" + "\n".join(relevant_snippets)
        except Exception as e:
            print(f"⚠️ Error extrayendo contexto git: {e}")
            
        return code_context

    def evolutionary_bounty_searcher(self, keywords=None):
        print("🔍 [BUSCADOR REPUTACIONAL] Filtrando proyectos reales, plataformas verificadas y reputación alta...")
        added = 0
        real_findings = []
        
        # Búsquedas orientadas a labels de plataformas de bounties reales (Algora, Polar, Bug Bounty)
        queries = [
            'label:"bounty" is:issue is:open stars:>20',
            'label:"algora" is:issue is:open',
            'label:"polar" is:issue is:open',
            'label:"help wanted" label:"bounty" is:issue is:open'
        ]

        blacklisted = ["bounty-plaza", "income-", "cyber", "test/audit", "spam"]

        for q in queries:
            try:
                cmd = ["/usr/bin/gh", "search", "issues", "--state", "open", "--limit", "10", "--json", "repository,number,title,labels", q]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if res.returncode == 0 and res.stdout.strip():
                    data = json.loads(res.stdout)
                    for item in data:
                        repo = item.get("repository", {}).get("nameWithOwner", "")
                        issue_id = str(item.get("number", ""))
                        title = item.get("title", "")
                        
                        # Filtro de seguridad anti-spam
                        if any(b in repo.lower() or b in title.lower() for b in blacklisted):
                            continue

                        if repo and issue_id and repo != "None":
                            real_findings.append((repo, issue_id, title, "$150 USD (Est.)"))
            except Exception:
                pass

        # Persistencia limpia
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            for r, i, t, rw in real_findings:
                cur.execute("SELECT id FROM bounty_opportunities WHERE repo=? AND issue_id=?", (r, str(i)))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO bounty_opportunities (repo, issue_id, title, reward, status) VALUES (?, ?, ?, ?, 'PENDING')",
                        (r, str(i), t, rw)
                    )
                    added += 1
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error registrando en DB: {e}")

        print(f"✅ Buscador Reputacional finalizado. Se han incorporado {added} bounties de alta reputación.")
        return added

    def fetch_pending_bounties_from_db(self):
        results = []
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT repo, issue_id, title 
                FROM bounty_opportunities 
                WHERE repo IS NOT NULL AND repo != 'None' AND repo != '' AND status NOT IN ('RESOLVED', 'REJECTED') 
                ORDER BY id DESC 
                LIMIT 15;
            """)
            rows = cur.fetchall()
            conn.close()
            if rows:
                return [(str(r[0]), str(r[1]), str(r[2])) for r in rows if r[0] and r[0] != 'None']
        except Exception as e:
            print(f"⚠️ Error consultando pendientes: {e}")
        return [("soenneker/soenneker.libraries.whisper.ctranslate", "1", "[Bug]: Unicode support is incorrect")]

    def process_bounty_loop(self, repo, issue_id, title=""):
        print(f"\n================================================================================")
        print(f"🔄 INICIANDO ENJAMBRE TRIPLE: {repo}#{issue_id}")
        print(f"📝 Título: {title}")
        print("================================================================================")
        
        # Extracción profunda de código real del repositorio
        repo_ctx = self.clone_and_extract_context(repo, title)
        if not repo_ctx:
            repo_ctx = f"Repo: {repo}, Issue: {title}"

        q_prompt = f"Evaluar viabilidad técnica del issue '{title}' en {repo}.\n\nDATOS REALES DEL CÓDIGO Y PROYECTO:\n{repo_ctx[:2500]}"
        q_res = self.call_ollama_stream(self.queen_brains[0]["model"], "Q1", self.queen_brains[0]["role"], q_prompt)

        s1_ctx = f"Issue: {title}\nDictamen Q1: {q_res[:150]}\nContexto Proyecto:\n{repo_ctx[:1500]}"
        for brain in [b for b in self.brains if b.get("swarm") == 1]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], f"Analiza la arquitectura y archivos fuente:\n{s1_ctx[-1000:]}")
            self._save_debate(repo, issue_id, 1, brain["code"], brain["role"], res)

        s2_ctx = s1_ctx[-800:]
        for brain in [b for b in self.brains if b.get("swarm") == 2]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], f"Desarrolla parche/código para resolver el bug:\n{s2_ctx[-1000:]}")
            self._save_debate(repo, issue_id, 2, brain["code"], brain["role"], res)

        s3_ctx = s2_ctx[-800:]
        for brain in [b for b in self.brains if b.get("swarm") == 3]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], f"Audita la calidad del parche y asignación de recompensa:\n{s3_ctx[-1000:]}")
            self._save_debate(repo, issue_id, 3, brain["code"], brain["role"], res)

        self._update_bounty_state(repo, issue_id, "RESOLVED")
        print(f"\n✅ [COMPLETADO] Tri-Enjambre procesó {repo}#{issue_id} exitosamente.")

    def _save_debate(self, repo, issue_id, swarm, code, role, text):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO swarm_debates (repo, issue_id, swarm_layer, brain_code, role_name, response_text) VALUES (?, ?, ?, ?, ?, ?)",
                        (repo, issue_id, swarm, code, role, text[:500]))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _update_bounty_state(self, repo, issue_id, new_state):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("UPDATE bounty_opportunities SET status=? WHERE issue_id=? AND repo=?", (new_state, str(issue_id), repo))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def run_full_pipeline(self):
        targets = self.fetch_pending_bounties_from_db()
        for t in targets:
            self.process_bounty_loop(t[0], t[1], t[2] if len(t)>2 else "")

def run_daemon_loop():
    import time
    import sqlite3
    import traceback
    import re
    import inspect

    db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
    print("🟢 [DAEMON ART63] Bucle autónomo iniciado correctamente con issue_id.", flush=True)

    try:
        orchestrator = TriSwarmOrchestrator()
    except Exception as e:
        print(f"❌ Error al instanciar TriSwarmOrchestrator: {e}", flush=True)
        traceback.print_exc()
        return

    while True:
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT id, issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC LIMIT 1")
            row = c.fetchone()

            if not row:
                conn.close()
                time.sleep(5)
                continue

            task_id, issue_url, repo, title = row[0], row[1], row[2], row[3]
            c.execute("UPDATE bounty_opportunities SET status='PROCESSING' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()

            # Extraer issue_id desde la URL (ej. /issues/773 -> "773")
            issue_id = str(task_id)
            if issue_url:
                match = re.search(r'/(?:issues|pull)/(\d+)', str(issue_url))
                if match:
                    issue_id = match.group(1)

            print("", flush=True)
            print(f"🚀 [DAEMON] Procesando Tarea ID {task_id} (Issue #{issue_id}): {repo} -> {title}", flush=True)

            if hasattr(orchestrator, "process_bounty_loop"):
                sig = inspect.signature(orchestrator.process_bounty_loop)
                params = list(sig.parameters.keys())
                
                kwargs = {}
                if "repo" in params:
                    kwargs["repo"] = repo
                if "issue_id" in params:
                    kwargs["issue_id"] = issue_id
                elif "issue_url" in params:
                    kwargs["issue_url"] = issue_url
                if "title" in params:
                    kwargs["title"] = title

                orchestrator.process_bounty_loop(**kwargs)
            else:
                print("⚠️ El método process_bounty_loop no está disponible en TriSwarmOrchestrator.", flush=True)

            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE bounty_opportunities SET status='COMPLETED' WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            print(f"✅ [DAEMON] Tarea ID {task_id} finalizada y marcada como COMPLETED.", flush=True)
            print("", flush=True)

        except Exception as e:
            print(f"❌ Error en ciclo de trabajo del demonio: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    import sys, os
    if "--daemon" in sys.argv:
        run_daemon_loop()
    elif "--submenu" in sys.argv:
        if "show_bounty_submenu" in globals():
            show_bounty_submenu()
        elif "bounty_submenu" in globals():
            bounty_submenu()
        else:
            print("🎯 [SUBMENÚ BOUNTIES] Opción de gestión de base de datos activa.")
    else:
        mando_script = "/home/k1/ccia_workspace/ccia_mando_63.py"
        if os.path.exists(mando_script):
            os.execv(sys.executable, [sys.executable, mando_script])
        else:
            print(f"❌ Error: No se encontró el centro de mando en {mando_script}")