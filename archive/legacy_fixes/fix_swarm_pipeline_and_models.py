import json
import os
import sqlite3
import subprocess
import py_compile

# 1. Configurar los 15 cerebros con la mejor combinación científica/técnica
optimal_brains = [
    {"code": "1.1", "role": "Archi-Investigador", "icon": "🔍", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"},
    {"code": "1.2", "role": "Archi-Diseñador", "icon": "📐", "model": "ccia-reina-r1coder-14b:latest"},
    {"code": "1.3", "role": "Especialista Backend", "icon": "⚙️", "model": "ccia-coder-xl-14b:latest"},
    {"code": "1.4", "role": "Especialista Frontend", "icon": "🎨", "model": "ccia-coder-xl-14b:latest"},
    {"code": "1.5", "role": "Auditor Seguridad", "icon": "🛡️", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"},
    {"code": "2.1", "role": "Critico Código", "icon": "🧪", "model": "codestral:latest"},
    {"code": "2.2", "role": "Optimizador Rendimiento", "icon": "⚡", "model": "deepscaler:latest"},
    {"code": "2.3", "role": "Ingeniero Pruebas", "icon": "🎯", "model": "ccia-coder-xl-14b:latest"},
    {"code": "2.4", "role": "Redactor Docs", "icon": "📝", "model": "mistral-nemo:12b"},
    {"code": "2.5", "role": "Integrador API", "icon": "🔌", "model": "ccia-coder-xl-14b:latest"},
    {"code": "3.1", "role": "Arbitro Calidad", "icon": "⚖️", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"},
    {"code": "3.2", "role": "Estratega Bounties", "icon": "💰", "model": "ccia-reina-r1coder-14b:latest"},
    {"code": "3.3", "role": "Especialista DB", "icon": "🗄️", "model": "qwen2.5-coder:14b"},
    {"code": "3.4", "role": "Gestor Despliegue", "icon": "🚀", "model": "ccia-coder-xl-14b:latest"},
    {"code": "3.5", "role": "Reina Mando", "icon": "👑", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"}
]

optimal_queen_brains = [
    {"code": "Q1", "role": "Reina Gobernanza & Estrategia", "icon": "👑", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"},
    {"code": "Q2", "role": "Reina Calidad & Seguridad", "icon": "🛡️", "model": "richardyoung/deepseek-r1-32b-uncensored:latest"},
    {"code": "Q3", "role": "Reina Finanzas & Bounties", "icon": "💎", "model": "ccia-reina-r1coder-14b:latest"}
]

with open("/home/k1/ccia_workspace/swarm_brains_63.json", "w", encoding="utf-8") as f:
    json.dump(optimal_brains, f, indent=2, ensure_ascii=False)

with open("/home/k1/ccia_workspace/queen_brains_63.json", "w", encoding="utf-8") as f:
    json.dump(optimal_queen_brains, f, indent=2, ensure_ascii=False)

print("✅ Archivos swarm_brains_63.json y queen_brains_63.json actualizados con modelos óptimos.")

# 2. Inyección del motor de inferencia sin rodeos y ejecutor en cascada
def update_orquestator_pipeline(filepath):
    print(f"🛠️ Actualizando motor en cascada de TriSwarm en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pipeline_code = '''
    def call_ollama_direct(self, model, system_prompt, user_prompt):
        no_fluff_sys = (
            "STRICT SYSTEM DIRECTIVE: YOU ARE A SCIENTIFIC/TECHNICAL AGENT. "
            "DO NOT GREET. DO NOT SAY 'HELLO', 'SURE', OR 'I WOULD BE HAPPY TO HELP'. "
            "DO NOT APOLOGIZE. OUTPUT ONLY DIRECT TECHNICAL DATA, CODE, OR CONCISE ANALYSIS."
            "\\n\\n" + system_prompt
        )
        try:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": no_fluff_sys},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            })
            res = subprocess.run(["curl", "-s", "-X", "POST", "http://localhost:11434/api/chat",
                                "-H", "Content-Type: application/json", "-d", payload],
                                capture_output=True, text=True, timeout=120)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"[Error en inferencia: {e}]"
        return "[Sin respuesta de Ollama]"

    def run_full_pipeline(self, repo="target/bounty-repo", issue_id="101"):
        print(f"\\n================================================================================")
        print(f"🚀 INICIANDO CICLO REAL TRI-SWARM EN CASCADA PARA {repo}#{issue_id}")
        print("================================================================================")
        
        # SWARM 1: INVESTIGACIÓN
        print("\\n🔍 [FASE 1] SWARM 1 (Investigación y Arquitectura)...")
        b1_1 = next((b for b in self.brains if b["code"] == "1.1"), self.brains[0])
        prompt1 = f"Analizar requerimientos técnicos e issue {repo}#{issue_id}. Definir plan de arquitectura."
        res1 = self.call_ollama_direct(b1_1["model"], b1_1["role"], prompt1)
        print(f"  [{b1_1['code']}] {b1_1['role']} ({b1_1['model']}):")
        print(f"  {res1[:250]}...\\n")

        # SWARM 2: DESARROLLO Y CÓDIGO
        print("⚙️ [FASE 2] SWARM 2 (Desarrollo y Generación de Código)...")
        b2_3 = next((b for b in self.brains if b["code"] == "2.3"), self.brains[7])
        prompt2 = f"Basado en este plan:\\n{res1[:300]}\\nGenerar código fuente y test unitario en bloques markdown."
        res2 = self.call_ollama_direct(b2_3["model"], b2_3["role"], prompt2)
        print(f"  [{b2_3['code']}] {b2_3['role']} ({b2_3['model']}):")
        print(f"  {res2[:250]}...\\n")

        # SWARM 3: AUDITORÍA DE CALIDAD
        print("⚖️ [FASE 3] SWARM 3 (Arbitraje y Calidad)...")
        b3_1 = next((b for b in self.brains if b["code"] == "3.1"), self.brains[10])
        prompt3 = f"Revisar el código generado:\\n{res2[:300]}\\nValidar vulnerabilidades, cobertura de pruebas y rendimiento."
        res3 = self.call_ollama_direct(b3_1["model"], b3_1["role"], prompt3)
        print(f"  [{b3_1['code']}] {b3_1['role']} ({b3_1['model']}):")
        print(f"  {res3[:250]}...\\n")

        # ENJAMBRE REINA: SUPERVISIÓN Y DECISIÓN FINAL
        print("👑 [FASE 4] GOBERNANZA ENJAMBRE REINA (Dictamen Final)...")
        q1 = getattr(self, "queen_brains", [{}])[0]
        q1_model = q1.get("model", "richardyoung/deepseek-r1-32b-uncensored:latest")
        prompt_q = f"Evaluar propuesta global:\\nInvestigación: {res1[:150]}\\nCódigo: {res2[:150]}\\nAuditoría: {res3[:150]}\\n¿Aprobar para PR/Envío?"
        res_q = self.call_ollama_direct(q1_model, "Reina Gobernanza Q1", prompt_q)
        print(f"  [Q1] Reina Gobernanza ({q1_model}):")
        print(f"  {res_q[:250]}...\\n")

        # GUARDAR REGISTROS
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bounty_swarm_history (repo, issue_id, status, created_at, swarm1_draft)
                VALUES (?, ?, 'SUCCESS', datetime('now'), ?);
            """, (repo, str(issue_id), f"REINA DICTAMEN:\\n{res_q}\\n\\nCÓDIGO:\\n{res2}"))
            conn.commit()
            conn.close()
            print("✅ Ejecució completada y registrada en DB (bounty_swarm_history).")
        except Exception as e:
            print(f"⚠️ Error guardando en DB: {e}")
'''

    if "def call_ollama_direct" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + pipeline_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

update_orquestator_pipeline("/home/k1/ccia_workspace/modules/art_63.py")
update_orquestator_pipeline("/home/k1/ccia_workspace/ccia_mando_63.py")
