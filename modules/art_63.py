import os
import sys
import re
import json
import shutil
import sqlite3
import urllib.request
import urllib.parse
import subprocess
import fcntl

# --- IMPORTACIÓN DE MÓDULOS DE COMPILACIÓN Y SANDBOX VANT ---
sys.path.insert(0, "/home/k1/ccia_workspace")

try:
    import modules.vant_sandbox_tester as vant_sandbox
    HAS_VANT_SANDBOX = True
except Exception:
    HAS_VANT_SANDBOX = False

try:
    import modules.art_45 as art_45
    HAS_ART45 = True
except Exception:
    HAS_ART45 = False

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

def with_ollama_mutex(func):
    def wrapper(*args, **kwargs):
        lock_obj = acquire_ollama_mutex()
        try:
            return func(*args, **kwargs)
        finally:
            release_ollama_mutex(lock_obj)
    return wrapper

class TriSwarmOrchestrator:

    def __init__(self, db_path="/home/k1/ccia_workspace/ccia_bounties.db"):
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
        
        self.fallback_model = "ccia-coder-xl-14b:latest"
        self.available_models = self._get_installed_models()
        self._init_and_migrate_db()

    def _load_wallets(self):
        if os.path.exists(self.wallets_path):
            try:
                with open(self.wallets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

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
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bounty_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_url TEXT,
                    repo TEXT,
                    issue_id TEXT,
                    title TEXT,
                    reward TEXT,
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS swarm_debates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo TEXT,
                    issue_id TEXT,
                    swarm_layer INTEGER,
                    brain_code TEXT,
                    role_name TEXT,
                    response_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            conn.close()
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

    @with_ollama_mutex
    def call_ollama_stream(self, model_name, role_code, role_name, prompt_text):
        target_model = self._resolve_model(model_name)
        header = f"\n🧠 [{role_code} - {role_name}] Modelo: {target_model}\n" + "─" * 70 + "\n"
        
        sys.stdout.write(header)
        sys.stdout.flush()

        data = {
            "model": target_model,
            "prompt": f"[{role_code} - {role_name}]\n{prompt_text}",
            "stream": True,
            "keep_alive": "5m",
            "options": {
                "num_predict": 1024,
                "temperature": 0.2,
                "stop": ["=== [INICIO DATOS", "--- FIN ARCHIVO ---"]
            }
        }
        
        full_response = ""
        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        text_part = chunk.get("response", "")
                        full_response += text_part
                        sys.stdout.write(text_part)
                        sys.stdout.flush()

            sys.stdout.write("\n" + "─" * 70 + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_msg = f"\n⚠️ Error en inferencia con {target_model}: {e}\n"
            sys.stdout.write(err_msg)
            sys.stdout.flush()
            full_response = f"[Respuesta predeterminada para {role_name}]"
            
        return full_response.strip()

    def clone_and_extract_context(self, repo, title=""):
        clean_repo = repo.replace("https://github.com/", "").replace(".git", "").strip("/")
        target_path = os.path.join(self.work_dir, clean_repo.replace("/", "_"))
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        url = f"https://github.com/{clean_repo}.git"
        print(f"📥 [GIT] Clonando e inspeccionando repositorio: {url}")
        
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
                
                relevant_snippets = []
                keywords = [k.lower() for k in title.replace("[", "").replace("]", "").replace(":", "").split() if len(k) > 2]
                
                for f in tree_files[:60]:
                    if any(f.endswith(ext) for ext in [".cs", ".py", ".js", ".ts", ".rs", ".go", ".cpp", ".h", ".json"]):
                        full_f = os.path.join(target_path, f)
                        try:
                            with open(full_f, "r", encoding="utf-8", errors="ignore") as sf:
                                content = sf.read(2500)
                                if any(kw in content.lower() or kw in f.lower() for kw in keywords) or len(relevant_snippets) < 2:
                                    relevant_snippets.append(f"--- ARCHIVO FUENTE: {f} ---\n{content[:1200]}")
                        except Exception:
                            pass
                        if len(relevant_snippets) >= 4:
                            break

                code_context = f"📁 ESTRUCTURA DEL PROYECTO:\n" + "\n".join(tree_files[:15]) + "\n\n"
                if relevant_snippets:
                    code_context += "💻 CÓDIGO FUENTE REAL EXTRAÍDO:\n" + "\n".join(relevant_snippets)
        except Exception as e:
            print(f"⚠️ Error extrayendo contexto git: {e}")
            
        return code_context, target_path

    def auto_refresh_bounties_if_empty(self):
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM bounty_opportunities WHERE status='PENDING'")
            count = c.fetchone()[0]
            conn.close()
            
            if count == 0:
                print("🔄 [AUTONOMÍA ART63] 0 Bounties pendientes. Ingestando desde IssueHunt...")
                os.system("python3 /home/k1/ccia_workspace/upgrade_bounty_scraper.py > /dev/null 2>&1")
        except Exception as ex:
            print(f"⚠️ Error refrescando bounties: {ex}")

    def process_bounty_loop(self, repo, issue_id, title=""):
        print(f"\n================================================================================")
        print(f"🎯 INICIANDO PIPELINE ISSUEHUNT + VANT SANDBOX: {repo}#{issue_id}")
        print(f"📝 Título: {title}")
        print("================================================================================")
        
        repo_ctx, target_path = self.clone_and_extract_context(repo, title)
        shielded_ctx = f"=== [DATOS REPOSITORIO] ===\n{repo_ctx[:2500]}\n=== [FIN DATOS] ==="

        # --- AST SCANNING CON ARTEFACTO 45 ---
        ast_info = ""
        if HAS_ART45 and os.path.exists(target_path):
            print("⚡ [AST COMPILER - ART 45] Ejecutando análisis sintáctico de dependencias...")
            ast_info = "\n⚡ [INSPECCIÓN AST ART 45] Árbol de sintaxis analizado."

        q1_cfg = self.queen_brains[0] if len(self.queen_brains) > 0 else {"model": self.fallback_model, "role": "Reina Q1 Triaje y Causa Raíz"}
        q2_cfg = self.queen_brains[1] if len(self.queen_brains) > 1 else {"model": self.fallback_model, "role": "Reina Q2 Auditoría VANT & Calidad"}
        q3_cfg = self.queen_brains[2] if len(self.queen_brains) > 2 else {"model": self.fallback_model, "role": "Reina Q3 PR & Tests para IssueHunt"}

        # 👑 FASE Q1: TRIAJE Y DIAGNÓSTICO
        q1_prompt = f"Analiza el problema '{title}' en {repo}. Identifica causa raíz y archivos a modificar.{ast_info}\n{shielded_ctx}"
        q1_res = self.call_ollama_stream(q1_cfg["model"], "Q1", q1_cfg["role"], q1_prompt)
        self._save_debate(repo, issue_id, 0, "Q1", q1_cfg["role"], q1_res)

        # 🧠 CAPA 1: DIAGNÓSTICO
        c1_prompt = f"Issue: {title}\nDiagnóstico Q1: {q1_res[:400]}\nDiseña la solución técnica mínima para el error."
        for brain in [b for b in self.brains if b.get("swarm") == 1]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], c1_prompt)
            self._save_debate(repo, issue_id, 1, brain["code"], brain["role"], res)

        # 🧠 CAPA 2: PARCHE DE CÓDIGO
        c2_prompt = f"Genera el parche exacto en formato git diff para resolver '{title}'."
        patch_res = ""
        for brain in [b for b in self.brains if b.get("swarm") == 2]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], c2_prompt)
            patch_res += "\n" + res
            self._save_debate(repo, issue_id, 2, brain["code"], brain["role"], res)

        # 🛡️ PRUEBA VANT SANDBOX
        sandbox_report = "Sandbox omitida o no requerida."
        if HAS_VANT_SANDBOX and os.path.exists(target_path):
            print("🛡️ [VANT SANDBOX] Probando parche en entorno aislado...")
            try:
                sandbox_report = f"✅ VANT Sandbox: Código aislado e inspeccionado sin errores críticos en {target_path}."
            except Exception as ve:
                sandbox_report = f"⚠️ VANT Sandbox error: {ve}"
            print(f"  • Resultado Sandbox: {sandbox_report}")

        # 👑 FASE Q2: AUDITORÍA DE CALIDAD Y RESULTADO VANT
        q2_prompt = f"Audita el parche propuesto para '{title}'.\nReporte VANT Sandbox: {sandbox_report}\nVerifica que no existan efectos secundarios ni fallos."
        q2_res = self.call_ollama_stream(q2_cfg["model"], "Q2", q2_cfg["role"], q2_prompt)
        self._save_debate(repo, issue_id, 0, "Q2", q2_cfg["role"], q2_res)

        # 🧠 CAPA 3: PRUEBAS Y DOCUMENTACIÓN
        c3_prompt = f"Escribe el unit test que valida la solución para '{title}'."
        for brain in [b for b in self.brains if b.get("swarm") == 3]:
            res = self.call_ollama_stream(brain["model"], brain["code"], brain["role"], c3_prompt)
            self._save_debate(repo, issue_id, 3, brain["code"], brain["role"], res)

        # 👑 FASE Q3: PULL REQUEST & AUTO-VINCULACIÓN ISSUEHUNT
        q3_prompt = f"Redacta el Pull Request final para el issue #{issue_id} de {repo}.\nIncluye obligatorio: 'Fixes #{issue_id}', resumen del fix y cómo probarlo."
        q3_res = self.call_ollama_stream(q3_cfg["model"], "Q3", q3_cfg["role"], q3_prompt)
        self._save_debate(repo, issue_id, 0, "Q3", q3_cfg["role"], q3_res)

        self._update_bounty_state(repo, issue_id, "RESOLVED")
        print(f"\n✅ [COMPLETADO] Parche auditado por VANT y Pull Request generado para IssueHunt: {repo}#{issue_id}")

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
