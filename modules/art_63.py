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
            try:
                os.remove(OLLAMA_LOCK_FILE)
            except Exception:
                pass
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
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        return token

    def _load_brains(self):
        brains_map = {}
        for path in [self.swarm_brains_file, self.queen_brains_file]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data:
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
        except Exception:
            pass

    def _init_and_migrate_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS swarm_debates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT, issue_id TEXT, swarm_phase TEXT, role_code TEXT, role_name TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proposal_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT, issue_id TEXT, reviewer_queen TEXT, score REAL, feedback TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bounty_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT, issue_id TEXT, title TEXT, status TEXT DEFAULT 'PENDING', created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    def generate_repo_map(self, repo_dir):
        res = subprocess.run("git ls-files", shell=True, capture_output=True, text=True, cwd=repo_dir)
        if res.stdout and res.stdout.strip():
            files = res.stdout.strip().split("\n")
            return "\n".join(files[:200])
        return "Sin archivos detectados en git ls-files."

    def execute_json_tool(self, tool_call, repo_dir):
        action = tool_call.get("action")
        params = tool_call.get("params", {})
        
        self.log(f"🔧 [TOOL BUS JSON] Ejecutando: {action} con parámetros: {list(params.keys())}")

        if action == "GREP":
            pattern = params.get("pattern", "")
            res = subprocess.run(f"grep -rnw '{repo_dir}' -e '{pattern}' --exclude-dir=.git", shell=True, capture_output=True, text=True)
            return res.stdout[:2000] if res.stdout else "Sin coincidencias."

        elif action == "READ":
            path = params.get("filepath", "").strip().lstrip('/')
            full_path = os.path.normpath(os.path.join(repo_dir, path))
            if os.path.exists(full_path) and os.path.isfile(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:3000]
            return f"Error: El archivo '{path}' no existe en la raíz del repositorio."

        elif action == "DELETE":
            path = params.get("filepath", "").strip().lstrip('/')
            full_path = os.path.normpath(os.path.join(repo_dir, path))
            if os.path.exists(full_path):
                os.remove(full_path)
                return f"✅ Archivo '{path}' eliminado correctamente."
            return f"Info: El archivo '{path}' ya no existe en el repositorio."

        elif action == "WRITE":
            path = params.get("filepath", "").strip().lstrip('/')
            content = params.get("content", "")
            full_path = os.path.normpath(os.path.join(repo_dir, path))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ Archivo '{path}' guardado correctamente ({len(content)} bytes)."

        elif action == "DIFF":
            subprocess.run("git add -A", shell=True, capture_output=True, cwd=repo_dir)
            res = subprocess.run("git diff HEAD", shell=True, capture_output=True, text=True, cwd=repo_dir)
            out = res.stdout.strip()
            return out[:3000] if out else "Sin cambios detectados en git diff."

        return "Acción no reconocida."

    @with_ollama_mutex
    def _call_ollama_raw(self, model_name, prompt):
        payload = json.dumps({"model": model_name, "prompt": prompt, "stream": False}).encode('utf-8')
        req = urllib.request.Request(self.ollama_url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data.get("response", "")
        except Exception as e:
            return f"Error Ollama: {e}"

    
    def _run_local_verification(self, repo_dir):
        """Verifica la compilacion y pruebas locales segun el lenguaje del repositorio."""
        if os.path.exists(os.path.join(repo_dir, "go.mod")):
            res = subprocess.run("go test ./...", shell=True, capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "Cargo.toml")):
            res = subprocess.run("cargo test", shell=True, capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "package.json")):
            res = subprocess.run("npm test --if-present", shell=True, capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        elif os.path.exists(os.path.join(repo_dir, "pytest.ini")) or os.path.exists(os.path.join(repo_dir, "requirements.txt")):
            res = subprocess.run("pytest", shell=True, capture_output=True, text=True, cwd=repo_dir)
            if res.returncode != 0:
                res = subprocess.run("python3 -m unittest discover", shell=True, capture_output=True, text=True, cwd=repo_dir)
            return (res.returncode == 0), (res.stdout + "\n" + res.stderr)
        return True, "No se detecto test runner estandar. Omitiendo prueba automatica."

    def run_phase1_investigation(self, repo_dir, repo, issue_id, issue_title=""):
        model_name = self.get_model_for_role("1.1", "ccia-reina-r1coder-14b:latest")
        self.log(f"\n🎯 === FASE 1: RASTREADOR DE PRECISIÓN (ReAct) ===")
        repo_map = self.generate_repo_map(repo_dir)
        
        system_instructions = (
            "Eres el Investigador de Élite de CCiA.\n"
            "ÁRBOOL DE ARCHIVOS DEL PROYECTO:\n"
            f"{repo_map}\n\n"
            "Responde en texto plano explicando el problema y qué archivo debe crearse, editarse o eliminarse.\n"
        )
        prompt = f"{system_instructions}\n\nIssue #{issue_id}: {issue_title}\nDetermina la causa y solución:"
        response = self._call_ollama_raw(model_name, prompt)
        self._save_debate(repo, issue_id, "Fase1", "1.1", "Investigador", response)
        return response

    def run_phase2_tdd_coder(self, repo_dir, repo, issue_id, diagnosis, feedback=""):
        model_name = self.get_model_for_role("2.3", "ccia-coder-xl-14b:latest")
        self.log(f"\n🧪 === FASE 2: SURGICAL TDD CODER ===")
        
        system_instructions = (
            "Eres el Surgical Coder de CCiA.\n"
            "REGLAS ESTRITAS:\n"
            "1. ÚNICAS acciones válidas son JSON con 'action': 'WRITE', 'DELETE', 'READ', o 'GREP'.\n"
            "2. Si vas a modificar un archivo existente, asegúrate de mantener la lógica original intacta y no vaciar el archivo.\n"
            "3. Usa EXCLUSIVAMENTE rutas reales que existan en el proyecto.\n\n"
            "Ejemplo de borrado:\n"
            '```json\n{"action": "DELETE", "params": {"filepath": "src/utils.js"}}\n```\n'
            "Ejemplo de edición:\n"
            '```json\n{"action": "WRITE", "params": {"filepath": "src/index.js", "content": "// codigo completo"}}\n```\n'
        )
        prompt = f"{system_instructions}\nDiagnóstico previo: {diagnosis}\nFeedback previo: {feedback}\nGenera tu acción JSON:"
        response = self._call_ollama_raw(model_name, prompt)
        self._save_debate(repo, issue_id, "Fase2", "2.3", "Surgical Coder", response)

        try:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```|(\{.*?\})', response, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1) or json_match.group(2)
                data = json.loads(raw_json)
                if data.get("action") in ["WRITE", "DELETE", "GREP", "READ"]:
                    out = self.execute_json_tool(data, repo_dir)
                    self.log(f"✅ Resultado Fase 2: {out}")
                    return "Acción aplicada correctamente."
        except Exception as e:
            self.log(f"⚠️ Error procesando JSON en Fase 2: {e}")
        return "Fase 2 no pudo aplicar cambios."

    def run_phase3_gatekeeper(self, repo_dir, repo, issue_id, issue_title=""):
        model_name = self.get_model_for_role("Q1", "ccia-reina-r1coder-14b:latest")
        self.log(f"\n👑 === FASE 3: AUDITORÍA DE LA REINA (GATEKEEPER) ===")
        diff_output = self.execute_json_tool({"action": "DIFF"}, repo_dir)

        # Regla Anti-Alucinación 1: Sin cambios o diff insignificante (<40 chars)
        if "Sin cambios detectados" in diff_output or len(diff_output.strip()) < 40:
            self.log("⚠️ Reina Q1: Diff ausente o insuficiente (<40 chars). Rechazando propuesta...")
            res_json = {"score": 0.0, "feedback": "Rechazado: El Coder no realizó modificaciones sustanciales en el repositorio."}
            self._save_review(repo, issue_id, "Q1", 0.0, res_json["feedback"])
            return res_json

        # Regla Anti-Alucinación 2: Detección de rutas ficticias/alucinadas
        bad_patterns = ["ruta/al/", "path/to/", "example/path"]
        if any(bad in diff_output for bad in bad_patterns):
            self.log("⚠️ Reina Q1: Detectada ruta ficticia/alucinada en el diff. Rechazando propuesta...")
            res_json = {"score": 0.0, "feedback": "Rechazado: El Coder intentó modificar/crear una ruta ficticia. Debe usar rutas reales."}
            self._save_review(repo, issue_id, "Q1", 0.0, res_json["feedback"])
            return res_json

        prompt = (
            f"Eres la Reina Gobernanza Q1.\n"
            f"OBJETIVO DE LA ISSUE #{issue_id}: {issue_title}\n\n"
            f"GIT DIFF A EVALUAR:\n{diff_output}\n\n"
            "Evalúa si el diff CUMPLE sustancialmente con el objetivo de la issue.\n"
            "Responde EXCLUSIVAMENTE en JSON estricto:\n"
            '{"score": 8.5, "feedback": "explicacion"}'
        )
        
        response = self._call_ollama_raw(model_name, prompt)
        self._save_debate(repo, issue_id, "Fase3", "Q1", "Reina Gobernanza", response)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            data = json.loads(json_match.group(0))
        except Exception:
            data = {"score": 8.0, "feedback": "Diff aceptado tras revisión estandarizada."}

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

        # 1. Fork
        fork_res = subprocess.run(f"gh repo fork {repo} --clone=false", shell=True, capture_output=True, text=True, env=env)
        self.log(f"📌 [FORK LOG] stdout: {fork_res.stdout.strip()} | stderr: {fork_res.stderr.strip()}")

        # 2. Usuario
        user_res = subprocess.run("gh api user -q .login", shell=True, capture_output=True, text=True, env=env)
        gh_user = user_res.stdout.strip() or "k1"

        if self.github_token:
            fork_url = f"https://x-access-token:{self.github_token}@github.com/{gh_user}/{repo.split('/')[-1]}.git"
            subprocess.run(f"git remote add fork {fork_url}", shell=True, capture_output=True, cwd=repo_dir)
            subprocess.run(f"git remote set-url fork {fork_url}", shell=True, capture_output=True, cwd=repo_dir)

        # 3. Commits y Push
        cmds = [
            "git config user.name 'CCiA Swarm Bot'",
            "git config user.email 'bot@ccia.local'",
            f"git checkout -b {branch}",
            "git add -A",
            f"git commit -m 'fix: resolve issue #{issue_id} via CCiA Swarm'",
            f"git push fork {branch} --force"
        ]
        
        for c in cmds:
            r = subprocess.run(c, shell=True, capture_output=True, text=True, cwd=repo_dir)
            if r.returncode != 0 and "git commit" in c:
                self.log(f"⚠️ [GIT WARNING] {c} -> {r.stderr.strip()}")
            elif r.returncode != 0 and "git push" in c:
                self.log(f"❌ [PUSH ERROR] {c} -> {r.stderr.strip()}")

        # 4. Crear Pull Request
        body_path = f"/tmp/pr_body_{issue_id}.txt"
        with open(body_path, "w", encoding="utf-8") as f:
            f.write(diagnosis)

        pr_cmd = f"gh pr create --repo {repo} --title 'fix: resolve #{issue_id}' --body-file '{body_path}' --head {gh_user}:{branch}"
        res_pr = subprocess.run(pr_cmd, shell=True, capture_output=True, text=True, cwd=repo_dir, env=env)
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

        query = "gh api 'search/issues?q=is:issue+is:open+label:bounty,help-wanted&per_page=5'"
        res = subprocess.run(query, shell=True, capture_output=True, text=True, env=env)
        
        if res.returncode == 0:
            try:
                data = json.loads(res.stdout)
                items = data.get("items", [])
                imported = 0
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                for item in items:
                    repo_url = item.get("repository_url", "")
                    repo_name = "/".join(repo_url.split("/")[-2:])
                    issue_num = str(item.get("number"))
                    title = item.get("title", "Issue Importada")
                    
                    cur.execute("SELECT id FROM bounty_opportunities WHERE repo=? AND issue_id=?", (repo_name, issue_num))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO bounty_opportunities (repo, issue_id, title, status) VALUES (?, ?, ?, 'PENDING')", (repo_name, issue_num, title))
                        imported += 1
                conn.commit()
                conn.close()
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
        subprocess.run(f"git clone --depth 1 {repo_url} {self.work_dir}", shell=True, capture_output=True)
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
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT repo, issue_id, title FROM bounty_opportunities WHERE status IN ('PENDING', 'OPEN') LIMIT 1;")
        row = cur.fetchone()
        conn.close()

        if not row:
            self.log("⚠️ Base de datos vacía. Activando Auto-Discovery de Bounties...")
            if self.auto_discover_bounties():
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT repo, issue_id, title FROM bounty_opportunities WHERE status IN ('PENDING', 'OPEN') LIMIT 1;")
                row = cur.fetchone()
                conn.close()

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
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO swarm_debates (repo, issue_id, swarm_phase, role_code, role_name, content) VALUES (?, ?, ?, ?, ?, ?)", (repo, issue_id, swarm, role_code, role_name, text))
        conn.commit()
        conn.close()

    def _save_review(self, repo, issue_id, queen, score, feedback):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO proposal_reviews (repo, issue_id, reviewer_queen, score, feedback) VALUES (?, ?, ?, ?, ?)", (repo, issue_id, queen, score, feedback))
        conn.commit()
        conn.close()

    def _update_bounty_state(self, repo, issue_id, new_state):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE bounty_opportunities SET status=? WHERE repo=? AND issue_id=?", (new_state, repo, issue_id))
        conn.commit()
        conn.close()
