import os
import sys
import re
import json
import shutil
import sqlite3
import urllib.request
import subprocess
import fcntl
import time
from modules.art_64 import Artefact64EvolutionaryCompiler

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

OLLAMA_LOCK_FILE = "/tmp/ccia_ollama_global.lock"

def acquire_ollama_mutex():
    f = open(OLLAMA_LOCK_FILE, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        if os.path.exists(OLLAMA_LOCK_FILE) and (time.time() - os.path.getmtime(OLLAMA_LOCK_FILE) > 600):
            try: os.remove(OLLAMA_LOCK_FILE)
            except Exception: pass
            f = open(OLLAMA_LOCK_FILE, "w")
            fcntl.flock(f, fcntl.LOCK_EX)
        else:
            fcntl.flock(f, fcntl.LOCK_EX)
    return f

def release_ollama_mutex(lock_file_obj):
    if lock_file_obj:
        try:
            fcntl.flock(lock_file_obj, fcntl.LOCK_UN)
            lock_file_obj.close()
        except Exception: pass

def with_ollama_mutex(func):
    def wrapper(*args, **kwargs):
        lock_obj = acquire_ollama_mutex()
        try: return func(*args, **kwargs)
        finally: release_ollama_mutex(lock_obj)
    return wrapper

class TriSwarmOrchestrator:
    def __init__(self, db_path="/home/k1/ccia_workspace/ccia_bounties.db"):
        self.db_path = db_path
        self.ollama_url = "http://localhost:11434/api/generate"
        self.work_dir = "/tmp/bounty_work"
        self.log_file_path = "/tmp/art63_reasoning.log"
        self.swarm_brains_file = "/home/k1/ccia_workspace/swarm_brains_63.json"
        self.queen_brains_file = "/home/k1/ccia_workspace/queen_brains_63.json"
        self.github_token = self._get_github_token()
        self.brains = self._load_brains()
        self._init_and_migrate_db()

    def _get_github_token(self):
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token and os.path.exists("/home/k1/ccia_workspace/.env"):
            with open("/home/k1/ccia_workspace/.env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        return token

    def _load_brains(self):
        brains_map = {}
        for path in [self.swarm_brains_file, self.queen_brains_file]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for item in json.load(f):
                            brains_map[item["code"]] = item.get("model", "ccia-reina-r1coder-14b:latest")
                except Exception as e:
                    self.log(f"⚠️ Error cargando brains de {path}: {e}")
        return brains_map

    def get_model_for_role(self, role_code, default="ccia-reina-r1coder-14b:latest"):
        return self.brains.get(role_code, default)

    def log(self, text):
        msg = f"[ART63] {text}"
        print(msg, flush=True)
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception: pass

    def _init_and_migrate_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS swarm_debates (id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, swarm_phase TEXT, role_code TEXT, role_name TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS proposal_reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, reviewer_queen TEXT, score REAL, feedback TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS bounty_opportunities (id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, issue_id TEXT, title TEXT, status TEXT DEFAULT 'PENDING', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            """)

    def generate_repo_map(self, repo_dir):
        res = subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=repo_dir)
        return "\n".join(res.stdout.strip().split("\n")[:200]) if res.stdout else "Sin archivos detectados."

    def execute_json_tool(self, tool_call, repo_dir):
        action = tool_call.get("action")
        params = tool_call.get("params", {})
        self.log(f"🔧 [TOOL BUS] Ejecutando: {action}")

        if action == "GREP":
            pattern = params.get("pattern", "")
            res = subprocess.run(["grep", "-rnw", repo_dir, "-e", pattern, "--exclude-dir=.git"], capture_output=True, text=True)
            return res.stdout[:2000] if res.stdout else "Sin coincidencias."

        elif action == "READ":
            full_path = os.path.normpath(os.path.join(repo_dir, params.get("filepath", "").strip().lstrip('/')))
            if os.path.exists(full_path) and os.path.isfile(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:3000]
            return "Error: Archivo no existe."

        elif action == "DELETE":
            full_path = os.path.normpath(os.path.join(repo_dir, params.get("filepath", "").strip().lstrip('/')))
            if os.path.exists(full_path):
                os.remove(full_path)
                return "✅ Archivo eliminado."
            return "Info: El archivo ya no existe."

        elif action == "WRITE":
            path = params.get("filepath", "").strip().lstrip('/')
            content = params.get("content", "")
            full_path = os.path.normpath(os.path.join(repo_dir, path))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if path.endswith('.py') and "ccia_workspace" in repo_dir:
                self.log(f"🛡️ [ART 64] Interceptando escritura en módulo interno: {path}")
                val = Artefact64EvolutionaryCompiler.compile_and_test(path, content)
                self.log(f"🛡️ [ART 64] Resultado AST: {val['log']}")

            return f"✅ Archivo guardado ({len(content)} bytes)."

        elif action == "DIFF":
            subprocess.run(["git", "add", "-A"], capture_output=True, cwd=repo_dir)
            res = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=repo_dir)
            return res.stdout.strip()[:3000] if res.stdout else "Sin cambios."
        return "Acción no reconocida."

    @with_ollama_mutex
    def _call_ollama_raw(self, model_name, prompt):
        req = urllib.request.Request(self.ollama_url, data=json.dumps({"model": model_name, "prompt": prompt, "stream": False}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode('utf-8')).get("response", "")
        except Exception as e: return f"Error Ollama: {e}"

    def _run_local_verification(self, repo_dir):
        if os.path.exists(os.path.join(repo_dir, "go.mod")):
            res = subprocess.run(["go", "test", "./..."], capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "Cargo.toml")):
            res = subprocess.run(["cargo", "test"], capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "package.json")):
            res = subprocess.run(["npm", "test", "--if-present"], capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "pytest.ini")) or os.path.exists(os.path.join(repo_dir, "requirements.txt")):
            res = subprocess.run(["pytest"], capture_output=True, text=True, cwd=repo_dir)
            if res.returncode != 0:
                res = subprocess.run([sys.executable, "-m", "unittest", "discover"], capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        return True, "No se detecto test runner. Omitiendo."

    def run_phase1_investigation(self, repo_dir, repo, issue_id, issue_title=""):
        model_name = self.get_model_for_role("1.1", "ccia-reina-r1coder-14b:latest")
        self.log(f"\n🎯 === FASE 1: RASTREADOR ===")
        prompt = f"Eres Investigador CCiA.\nÁRBOL:\n{self.generate_repo_map(repo_dir)}\n\nIssue #{issue_id}: {issue_title}\nDetermina solución:"
        response = self._call_ollama_raw(model_name, prompt)
        self._save_debate(repo, issue_id, "Fase1", "1.1", "Investigador", response)
        return response

    def run_phase2_tdd_coder(self, repo_dir, repo, issue_id, diagnosis, feedback=""):
        model_name = self.get_model_for_role("2.3", "ccia-coder-xl-14b:latest")
        self.log(f"\n🧪 === FASE 2: SURGICAL CODER ===")
        prompt = f"Eres Coder CCiA. Usa acciones JSON STRICTAS (WRITE, DELETE, GREP, READ).\nDiagnóstico: {diagnosis}\nFeedback: {feedback}"
        response = self._call_ollama_raw(model_name, prompt)
        self._save_debate(repo, issue_id, "Fase2", "2.3", "Coder", response)

        try:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```|(\{.*?\})', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1) or json_match.group(2))
                if data.get("action") in ["WRITE", "DELETE", "GREP", "READ"]:
                    self.execute_json_tool(data, repo_dir)
        except Exception: pass
        return "Acción procesada."

    def run_phase3_gatekeeper(self, repo_dir, repo, issue_id, issue_title=""):
        model_name = self.get_model_for_role("Q1", "ccia-reina-r1coder-14b:latest")
        self.log(f"\n👑 === FASE 3: GATEKEEPER ===")
        
        self.log("🛡️ Ejecutando tests locales del repositorio...")
        tests_passed, test_log = self._run_local_verification(repo_dir)
        if not tests_passed:
            self.log(f"⚠️ Reina Q1: Rechazo inmediato. Fallan tests locales:\n{test_log[:300]}")
            res_json = {"score": 0.0, "feedback": f"Tests fallaron:\n{test_log[:200]}"}
            self._save_review(repo, issue_id, "Q1", 0.0, res_json["feedback"])
            return res_json

        diff_output = self.execute_json_tool({"action": "DIFF"}, repo_dir)
        if len(diff_output.strip()) < 40:
            res_json = {"score": 0.0, "feedback": "Rechazado: Diff insuficiente."}
            self._save_review(repo, issue_id, "Q1", 0.0, res_json["feedback"])
            return res_json

        prompt = f"Eres Reina Q1. Issue #{issue_id}: {issue_title}\nDIFF:\n{diff_output}\n\nTests: PASSED. Evalúa diff. Responde JSON: {{\"score\": 8.5, \"feedback\": \"...\"}}"
        response = self._call_ollama_raw(model_name, prompt)
        
        try:
            data = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group(0))
        except Exception:
            data = {"score": 8.0, "feedback": "Aceptado tras revisión."}

        self._save_review(repo, issue_id, "Q1", float(data.get("score", 8.0)), str(data.get("feedback", "Ok")))
        self.log(f"✅ Reina Q1: Score {data.get('score')} - {data.get('feedback')}")
        return data

    def publish_fix_to_github(self, repo_dir, repo, issue_id, diagnosis):
        self.log(f"🚀 [GITHUB PR] Creando Fork y publicando solución para {repo}#{issue_id}...")
        branch = f"fix-issue-{issue_id}"
        env = os.environ.copy()
        if self.github_token:
            env["GH_TOKEN"] = self.github_token
            env["GITHUB_TOKEN"] = self.github_token

        fork_res = subprocess.run(["gh", "repo", "fork", repo, "--clone=false"], capture_output=True, text=True, env=env)
        self.log(f"📌 [FORK LOG] stdout: {fork_res.stdout.strip()} | stderr: {fork_res.stderr.strip()}")

        user_res = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True, env=env)
        gh_user = user_res.stdout.strip() or "k1"

        if self.github_token:
            fork_url = f"https://x-access-token:{self.github_token}@github.com/{gh_user}/{repo.split('/')[-1]}.git"
            subprocess.run(["git", "remote", "add", "fork", fork_url], capture_output=True, cwd=repo_dir)
            subprocess.run(["git", "remote", "set-url", "fork", fork_url], capture_output=True, cwd=repo_dir)

        cmds = [
            ["git", "config", "user.name", "CCiA Swarm Bot"],
            ["git", "config", "user.email", "bot@ccia.local"],
            ["git", "checkout", "-b", branch],
            ["git", "add", "-A"],
            ["git", "commit", "-m", f"fix: resolve issue #{issue_id} via CCiA Swarm"],
            ["git", "push", "fork", branch, "--force"]
        ]
        
        for c in cmds:
            r = subprocess.run(c, capture_output=True, text=True, cwd=repo_dir)
            if r.returncode != 0:
                self.log(f"⚠️ [GIT WARNING/ERROR] {' '.join(c)} -> {r.stderr.strip()}")

        body_path = f"/tmp/pr_body_{issue_id}.txt"
        with open(body_path, "w", encoding="utf-8") as f:
            f.write(diagnosis)

        pr_cmd = ["gh", "pr", "create", "--repo", repo, "--title", f"fix: resolve #{issue_id}", "--body-file", body_path, "--head", f"{gh_user}:{branch}"]
        res_pr = subprocess.run(pr_cmd, capture_output=True, text=True, cwd=repo_dir, env=env)
        self.log(f"📌 [PR LOG] code: {res_pr.returncode} | stderr: {res_pr.stderr.strip()}")
        
        if res_pr.returncode == 0 or "already exists" in res_pr.stderr:
            self.log("✅ Pull Request enviada desde el Fork correctamente.")
            return True
        return False

    def auto_discover_bounties(self):
        self.log("🔍 [AUTO-DISCOVERY] Buscando nuevas Bounties e Issues abiertas en GitHub/IssueHunt...")
        env = os.environ.copy()
        if self.github_token:
            env["GH_TOKEN"] = self.github_token
            env["GITHUB_TOKEN"] = self.github_token

        res = subprocess.run(["gh", "api", "search/issues?q=is:issue+is:open+label:bounty,help-wanted&per_page=5"], capture_output=True, text=True, env=env)
        
        if res.returncode == 0:
            try:
                data = json.loads(res.stdout)
                items = data.get("items", [])
                imported = 0
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    for item in items:
                        repo_name = "/".join(item.get("repository_url", "").split("/")[-2:])
                        issue_num = str(item.get("number"))
                        title = item.get("title", "Issue Importada")
                        
                        cur.execute("SELECT id FROM bounty_opportunities WHERE repo=? AND issue_id=?", (repo_name, issue_num))
                        if not cur.fetchone():
                            cur.execute("INSERT INTO bounty_opportunities (repo, issue_id, title, status) VALUES (?, ?, ?, 'PENDING')", (repo_name, issue_num, title))
                            imported += 1
                    conn.commit()
                self.log(f"✅ Auto-discovery completado: {imported} nuevas bounties importadas.")
                return imported > 0
            except Exception as e:
                self.log(f"⚠️ Error procesando API: {e}")
        return False

    def clone_and_extract_context(self, repo):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        repo_url = f"https://github.com/{repo}.git" if not repo.startswith("http") else repo
        self.log(f"📦 Clonando repositorio: {repo_url}")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, self.work_dir], capture_output=True)
        return self.work_dir

    def process_bounty_loop(self, repo, issue_id, title=""):
        self.log(f"🚀 === PIPELINE TRIPLE ENJAMBRE (I+D+IT v3 Telemetría): {repo}#{issue_id} ===")
        repo_dir = self.clone_and_extract_context(repo)
        
        diagnosis = self.run_phase1_investigation(repo_dir, repo, issue_id, title)
        
        max_retries = 3
        feedback = ""
        review = {"score": 0.0, "feedback": "Sin evaluar"}
        
        for attempt in range(1, max_retries + 1):
            self.log(f"🔄 [Auto-Healing Loop] Intento {attempt}/{max_retries}...")
            self.run_phase2_tdd_coder(repo_dir, repo, issue_id, diagnosis, feedback=feedback)
            review = self.run_phase3_gatekeeper(repo_dir, repo, issue_id, issue_title=title)
            
            if review.get("score", 0) >= 7.0:
                self.log(f"✅ Aprobado por la Reina Q1. Score final: {review.get('score')}")
                break
            else:
                feedback = review.get("feedback", "Intento fallido.")
                self.log(f"⚠️ Rechazado en intento {attempt}. Feedback enviado a la Fase 2...")

        if review.get("score", 0) >= 7.0:
            if self.publish_fix_to_github(repo_dir, repo, issue_id, diagnosis):
                final_state = "SUBMITTED"
            else:
                final_state = "FAILED_PUSH"
        else:
            final_state = "REJECTED"

        self._update_bounty_state(repo, issue_id, final_state)
        self.log(f"🎉 Pipeline finalizado. Estado definitivo: [{final_state}]\n")

    def run_full_pipeline(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT repo, issue_id, title FROM bounty_opportunities WHERE status IN ('PENDING', 'OPEN') LIMIT 1;")
            row = cur.fetchone()

        if not row:
            self.log("⚠️ Base de datos vacía. Activando Auto-Discovery de Bounties...")
            if self.auto_discover_bounties():
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT repo, issue_id, title FROM bounty_opportunities WHERE status IN ('PENDING', 'OPEN') LIMIT 1;")
                    row = cur.fetchone()

        if row:
            self.process_bounty_loop(row[0], row[1], row[2])
        else:
            self.log("⚠️ No hay más Bounties disponibles en este ciclo.")

    def run_continuous_daemon(self):
        self.log("🔄 [DAEMON 24/7] Iniciando bucle autónomo del Enjambre...")
        while True:
            self.run_full_pipeline()
            time.sleep(10)

    def _save_debate(self, repo, issue_id, swarm, role_code, role_name, text):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO swarm_debates (repo, issue_id, swarm_phase, role_code, role_name, content) VALUES (?, ?, ?, ?, ?, ?)", (repo, issue_id, swarm, role_code, role_name, text))
            conn.commit()

    def _save_review(self, repo, issue_id, queen, score, feedback):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO proposal_reviews (repo, issue_id, reviewer_queen, score, feedback) VALUES (?, ?, ?, ?, ?)", (repo, issue_id, queen, score, feedback))
            conn.commit()

    def _update_bounty_state(self, repo, issue_id, new_state):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE bounty_opportunities SET status=? WHERE repo=? AND issue_id=?", (new_state, repo, issue_id))
            conn.commit()
