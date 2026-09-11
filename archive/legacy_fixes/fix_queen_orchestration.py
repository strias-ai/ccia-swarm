import json
import sqlite3
import urllib.request
import py_compile

def update_orchestrator_core(filepath):
    print(f"🛠️ Aplicando motor de orquestación dinámica y cliente HTTP nativo en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    core_code = '''
    def call_ollama_direct(self, model, system_prompt, user_prompt):
        no_fluff_sys = (
            "STRICT SYSTEM DIRECTIVE: YOU ARE A SCIENTIFIC/TECHNICAL AGENT. "
            "DO NOT GREET. DO NOT SAY 'HELLO', 'SURE', OR 'I WOULD BE HAPPY TO HELP'. "
            "DO NOT APOLOGIZE. OUTPUT ONLY DIRECT TECHNICAL DATA, CODE, OR CONCISE ANALYSIS.\\n\\n"
            + system_prompt
        )
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": no_fluff_sys},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"[Error en inferencia Ollama HTTP: {e}]"
        return "[Sin respuesta de Ollama]"

    def validate_antispam_output(self, raw_output):
        try:
            clean_str = raw_output.replace("```json", "").replace("```", "").strip()
            start = clean_str.find("{")
            end = clean_str.rfind("}")
            if start != -1 and end != -1:
                clean_str = clean_str[start:end+1]
            data = json.loads(clean_str)
            is_valid = data.get("valid", data.get("valida", True))
            reason = data.get("reason", data.get("razon", "Sin razón especificada"))
            return is_valid, reason
        except Exception:
            if "false" in raw_output.lower() or "spam" in raw_output.lower() or "inválid" in raw_output.lower():
                return False, "Patrón de spam o invalidez detectado en texto plano."
            return True, "OK"

    def run_full_pipeline(self, repo="target/bounty-repo", issue_id="101"):
        print(f"\\n================================================================================")
        print(f"🚀 INICIANDO CICLO DINÁMICO REINA TRI-SWARM PARA {repo}#{issue_id}")
        print("================================================================================")
        
        q1_model = getattr(self, "queen_brains", [{}])[0].get("model", "richardyoung/deepseek-r1-32b-uncensored:latest")
        b1_1 = next((b for b in self.brains if b["code"] == "1.1"), self.brains[0])
        b2_3 = next((b for b in self.brains if b["code"] == "2.3"), self.brains[7])
        b3_1 = next((b for b in self.brains if b["code"] == "3.1"), self.brains[10])

        # 1. FILTRO PREVIO REINA (CORTOCIRCUITO)
        print("\\n👑 [SUPERVISIÓN REINA] Validando viabilidad y antispam preliminar...")
        pre_check_prompt = f"Analizar viabilidad de bounty {repo}#{issue_id}. Responder ÚNICAMENTE un JSON estricto: {{\"valid\": true/false, \"reason\": \"explicacion\"}}"
        raw_pre = self.call_ollama_direct(q1_model, "Filtro AntiSpam Reina Q1", pre_check_prompt)
        is_valid, reason = self.validate_antispam_output(raw_pre)
        
        if not is_valid:
            print(f"🛑 [CORTOCIRCUITO REINA] Bounty descartado: {reason}")
            return

        # 2. SWARM 1: INVESTIGACIÓN
        print(f"\\n🔍 [FASE 1] SWARM 1 (Investigación - Modelo: {b1_1['model']})...")
        prompt1 = f"Analizar requerimientos e issue {repo}#{issue_id}. Generar plan técnico y estructura de archivos."
        res1 = self.call_ollama_direct(b1_1["model"], b1_1["role"], prompt1)
        print(f"  [{b1_1['code']}] {b1_1['role']}:\\n  {res1[:250]}...\\n")

        # 3. EVALUACIÓN INTERMEDIA REINA (SWARM 1 -> REINA)
        print("👑 [EVALUACIÓN INTERMEDIA REINA] Auditando propuesta de Swarm 1...")
        eval1_prompt = f"Evaluar propuesta técnica:\\n{res1[:400]}\\n¿Es correcta para proceder? Responder JSON {{\"valid\": true/false, \"reason\": \"...\"}}"
        raw_eval1 = self.call_ollama_direct(q1_model, "Reina Gobernanza Q1", eval1_prompt)
        v1, r1 = self.validate_antispam_output(raw_eval1)
        if not v1:
            print(f"⚠️ [REINA CORRECCIÓN] Reintentando Swarm 1 con feedback: {r1}")
            res1 = self.call_ollama_direct(b1_1["model"], b1_1["role"], f"{prompt1}\\nCORRECCIÓN REINA: {r1}")

        # 4. SWARM 2: DESARROLLO Y CÓDIGO
        print(f"⚙️ [FASE 2] SWARM 2 (Desarrollo y Código - Modelo: {b2_3['model']})...")
        prompt2 = f"Basado en el diseño:\\n{res1[:300]}\\nGenerar parches de código y pruebas unitarias."
        res2 = self.call_ollama_direct(b2_3["model"], b2_3["role"], prompt2)
        print(f"  [{b2_3['code']}] {b2_3['role']}:\\n  {res2[:250]}...\\n")

        # 5. SWARM 3: AUDITORÍA DE CALIDAD
        print(f"⚖️ [FASE 3] SWARM 3 (Calidad y Seguridad - Modelo: {b3_1['model']})...")
        prompt3 = f"Revisar código y tests:\\n{res2[:300]}\\nValidar seguridad, sintaxis y rendimiento."
        res3 = self.call_ollama_direct(b3_1["model"], b3_1["role"], prompt3)
        print(f"  [{b3_1['code']}] {b3_1['role']}:\\n  {res3[:250]}...\\n")

        # 6. DICTAMEN FINAL REINA Y REGISTRO DB
        print("👑 [FASE 4] DICTAMEN FINAL ENJAMBRE REINA...")
        q_final_prompt = f"Dictamen final para enviar PR.\\nInvestigación: {res1[:150]}\\nCódigo: {res2[:150]}\\nQA: {res3[:150]}"
        res_q = self.call_ollama_direct(q1_model, "Reina Gobernanza Q1", q_final_prompt)
        print(f"  [Q1] Dictamen Reina:\\n  {res_q[:250]}...\\n")

        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bounty_swarm_history (repo, issue_id, status, created_at, swarm1_draft)
                VALUES (?, ?, 'SUCCESS', datetime('now'), ?);
            """, (repo, str(issue_id), f"REINA DICTAMEN:\\n{res_q}\\n\\nCÓDIGO:\\n{res2}"))
            conn.commit()
            conn.close()
            print("✅ Ejecución del ciclo dinámico completada y registrada en DB.")
        except Exception as e:
            print(f"⚠️ Error guardando resultado en DB: {e}")
'''

    if "def call_ollama_direct" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + core_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y ACTUALIZADO EXITOSAMENTE.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

update_orchestrator_core("/home/k1/ccia_workspace/modules/art_63.py")
update_orchestrator_core("/home/k1/ccia_workspace/ccia_mando_63.py")
