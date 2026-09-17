import sys
import os
import json
import subprocess
import shlex
import sqlite3

sys.path.append('/home/k1/ccia_workspace/modules')
try:
    from swarm_middleware import process_task, save_successful_patch
    HAS_SWARM_MIDDLEWARE = True
except ImportError:
    HAS_SWARM_MIDDLEWARE = False

try:
    from art_65 import CCiASwarmGateway
except ImportError:
    CCiASwarmGateway = None

class CCiAGatewayBridge:
    """Cliente unificado A2A y Tool Bus para el enjambre CCiA."""

    @staticmethod
    def get_enriched_prompt_context(repo_path: str, prompt_template: str = "python_security_auditor.json") -> dict:
        inspection = {}
        if CCiASwarmGateway:
            inspection = CCiASwarmGateway.inspect_repository(repo_path)
            
        prompt_file = os.path.join("/home/k1/ccia_workspace/prompts", prompt_template)
        system_prompt = "Eres un asistente de ingeniería de software."
        
        if os.path.exists(prompt_file):
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    system_prompt = data.get("system_prompt", system_prompt)
            except Exception: pass

        return {
            "status": "SUCCESS",
            "system_prompt": system_prompt,
            "file_tree": inspection.get("file_tree", []),
            "code_snippets": inspection.get("code_snippets", {}),
            "total_files": len(inspection.get("file_tree", []))
        }

    @staticmethod
    def run_sandbox_validation(command: str, timeout: int = 15) -> dict:
        try:
            safe_cmd = shlex.split(command)
            res = subprocess.run(safe_cmd, capture_output=True, text=True, timeout=timeout)
            return {"success": res.returncode == 0, "exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Execution Timeout"}
        except Exception as e: return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}

    @staticmethod
    def dispatch_a2a_bus_message(sender_id: str, target_id: str, payload: dict) -> dict:
        return {"bus_status": "DELIVERED_TO_QUEUE", "sender": sender_id, "target": target_id, "payload_summary": list(payload.keys())}

    @staticmethod
    def fetch_memory_context(agent_id: str, topic: str) -> dict:
        """Extrae memoria real desde los debates del enjambre (university o bounties db)."""
        db_path = "/home/k1/ccia_workspace/ccia_bounties.db"
        nodes = []
        if os.path.exists(db_path):
            try:
                with sqlite3.connect(db_path) as conn:
                    cur = conn.cursor()
                    # Busca el tópico en el contenido de los debates
                    cur.execute("SELECT content FROM swarm_debates WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 3", (f"%{topic}%",))
                    rows = cur.fetchall()
                    nodes = [r[0][:200] + "..." for r in rows if r[0]]
            except Exception as e:
                nodes.append(f"Error DB: {str(e)}")
        
        return {
            "agent_id": agent_id,
            "topic": topic,
            "memory_nodes": nodes,
            "cache_hit": len(nodes) > 0
        }
