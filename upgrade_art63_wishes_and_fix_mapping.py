import os
import sys
import json
import subprocess

print("=" * 80)
print("🚀 INTEGRANDO DESEOS 1, 2 Y 4 + CORRIGIENDO PERSISTENCIA DE CEREBROS EN ART_63")
print("=" * 80)

# Directories
ws_dir = "/home/k1/ccia_workspace"
memory_dir = os.path.join(ws_dir, "swarm_memory")
os.makedirs(memory_dir, exist_ok=True)
config_json = os.path.join(memory_dir, "brain_models_config.json")

# 1. Crear configuración por defecto si no existe
default_brains = {
    "1.1": "huihui_ai/deepseek-r1-abliterated:14b",
    "1.2": "huihui_ai/deepseek-r1-abliterated:14b",
    "1.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "1.4": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "1.5": "dolphin-llama3:8b",
    "2.1": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.2": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "2.4": "mistral-nemo:12b",
    "2.5": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.1": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.2": "huihui_ai/deepseek-r1-abliterated:14b",
    "3.3": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.4": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "3.5": "huihui_ai/deepseek-r1-abliterated:14b",
    "Q1": "huihui_ai/deepseek-r1-abliterated:14b",
    "Q2": "huihui_ai/qwen2.5-coder-abliterate:14b",
    "Q3": "mistral-nemo:12b"
}

if not os.path.exists(config_json):
    with open(config_json, "w", encoding="utf-8") as f:
        json.dump(default_brains, f, indent=2)
    print("  ✅ Archivo swarm_memory/brain_models_config.json creado con mapa base.")

# 2. Inyectar Módulos de Deseos en modules/art_63.py
art63_path = os.path.join(ws_dir, "modules", "art_63.py")
with open(art63_path, "r", encoding="utf-8") as f:
    code = f.read()

wishes_code = '''
# ==============================================================================
# 🎅 MODULOS EXTENDIDOS: DESEOS 1, 2 Y 4 DEL ENJAMBRE ARTEFACTO 63
# ==============================================================================
import math
import urllib.request

class Artefact63GitHubPublisher:
    """DESEO 1: Publicador Automático de Pull Requests mediante gh CLI"""
    @staticmethod
    def publish_pull_request(repo_full_name, branch_name, commit_msg, pr_title, pr_body):
        try:
            # 1. Crear rama git y commit
            subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True)
            subprocess.run(["git", "add", "."], capture_output=True)
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
            
            # 2. Publicar PR vía gh CLI
            cmd = ["/usr/bin/gh", "pr", "create", "--repo", repo_full_name, "--title", pr_title, "--body", pr_body, "--head", branch_name]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return f"🟢 Pull Request publicado exitosamente: {res.stdout.strip()}"
            return f"⚠️ No se pudo enviar el PR (requiere repo fork/permisos): {res.stderr.strip()}"
        except Exception as e:
            return f"❌ Error enviando PR: {e}"

class Artefact63RAGEngine:
    """DESEO 2: Engine RAG de Código Local con nomic-embed-text de Ollama"""
    @staticmethod
    def get_embedding(text):
        try:
            url = "http://localhost:11434/api/embeddings"
            payload = json.dumps({"model": "nomic-embed-text:latest", "prompt": text[:1000]}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                return res.get("embedding", [])
        except Exception:
            return []

    @staticmethod
    def cosine_similarity(v1, v2):
        if not v1 or not v2: return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        m1 = math.sqrt(sum(a * a for a in v1))
        m2 = math.sqrt(sum(b * b for b in v2))
        return dot / (m1 * m2) if m1 and m2 else 0.0

    @classmethod
    def search_relevant_code(cls, query, code_chunks, top_k=3):
        q_emb = cls.get_embedding(query)
        if not q_emb:
            return code_chunks[:top_k]
        
        scored = []
        for chunk in code_chunks:
            c_emb = cls.get_embedding(chunk)
            score = cls.cosine_similarity(q_emb, c_emb)
            scored.append((score, chunk))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

class Artefact63PayoutListener:
    """DESEO 4: Verificador de Recompensas On-Chain (BTC / EVM)"""
    @staticmethod
    def check_btc_balance(btc_address):
        try:
            url = f"https://mempool.space/api/address/{btc_address}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
                return funded / 100000000.0
        except Exception:
            return 0.0
'''

if "class Artefact63GitHubPublisher:" not in code:
    code = wishes_code + "\n\n" + code

# Exportar variables globales para la inspección
if "BRAIN_MODEL_MAP = default_brains" not in code:
    code += "\n\nBRAIN_MODEL_MAP = " + json.dumps(default_brains) + "\n"

with open(art63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ Módulo modules/art_63.py actualizado con los Deseos 1, 2 y 4.")

# 3. Corregir ccia_mando_63.py para mapear los índices numéricos a nombres reales de Ollama
mando63_path = os.path.join(ws_dir, "ccia_mando_63.py")
with open(mando63_path, "r", encoding="utf-8") as f:
    mando_code = f.read()

# Inyectar guardado dinámico de string real
fix_mapping_code = '''
            if sel_brain and choice_idx:
                try:
                    idx = int(choice_idx)
                    if 1 <= idx <= len(installed_models):
                        selected_model_name = installed_models[idx - 1]
                        
                        # Cargar config existente
                        cfg_path = "/home/k1/ccia_workspace/swarm_memory/brain_models_config.json"
                        cfg = {}
                        if os.path.exists(cfg_path):
                            with open(cfg_path, "r") as f_in:
                                cfg = json.load(f_in)
                        
                        cfg[sel_brain] = selected_model_name
                        
                        with open(cfg_path, "w") as f_out:
                            json.dump(cfg, f_out, indent=2)
                            
                        print(f"\\n  🟢 [ÉXITO] Cerebro {sel_brain} configurado persistentemente con: {selected_model_name}")
                    else:
                        print("\\n  ⚠️ Índice fuera de rango.")
                except ValueError:
                    print("\\n  ⚠️ Entrada inválida.")
'''

if "selected_model_name = installed_models[idx - 1]" not in mando_code:
    mando_code = mando_code.replace('print(f"\\n  🟢 Cerebro {sel_brain} reconfigurado.")', fix_mapping_code)
    with open(mando63_path, "w", encoding="utf-8") as f:
        f.write(mando_code)
    print("  ✅ Traductor e integrador de índices en ccia_mando_63.py corregido.")

subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
subprocess.run([sys.executable, "-m", "py_compile", mando63_path], check=True)
print("  ✅ Compilación exitosa de todos los módulos.")
print("=" * 80)
