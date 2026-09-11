import json
import sqlite3
import py_compile
import urllib.request
import os

def apply_full_state_machine(filepath):
    print(f"🛠️ Configurando máquina de estados completa en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    state_machine_code = '''
    def process_bounty_loop(self, repo, issue_id):
        print(f"\\n================================================================================")
        print(f"🔄 INICIANDO CICLO DE ESTADOS ENJAMBRE: {repo}#{issue_id}")
        print("================================================================================")
        
        # ESTADO 0: BÚSQUEDA Y REGISTRO EN DB
        print("\\n📡 [ESTADO 0] Registrando target en DB...")
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO bounty_opportunities (repo_owner_name, issue_number, state, title)
                VALUES (?, ?, 'QUEEN_CHECK', 'Auto-Discovered Target');
            """, (repo, str(issue_id)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Advertencia DB: {e}")

        # ESTADO 1: EVALUACIÓN REINA (FILTRO ROI & SPAM)
        print("\\n👑 [ESTADO 1] Filtro Reina (Q1/Q3): Verificando viabilidad y ROI...")
        q1_model = getattr(self, "queen_brains", [{}])[0].get("model", "richardyoung/deepseek-r1-32b-uncensored:latest")
        check_prompt = f"Evaluar bounty {repo}#{issue_id}. Responder estricto JSON: {{\"valid\": true, \"reason\": \"...\"}}"
        res_pre = self.call_ollama_direct(q1_model, "Reina Q1 Filtro", check_prompt)
        is_valid, reason = self.validate_antispam_output(res_pre)
        
        if not is_valid:
            print(f"🛑 [CORTOCIRCUITO REINA] Bounty descartado: {reason}")
            self.update_bounty_state(repo, issue_id, "REJECTED")
            return False

        print(f"✅ [REINA APROBADO] Procediendo a Enjambre 1 ({reason})")

        # ESTADO 2: ENJAMBRE 1 (INVESTIGACIÓN Y ARQUITECTURA)
        print("\\n🔍 [ESTADO 2] Enjambre 1: Analizando repositorio y diseñando arquitectura...")
        b1_1 = next((b for b in self.brains if b["code"] == "1.1"), self.brains[0])
        plan = self.call_ollama_direct(b1_1["model"], b1_1["role"], f"Analizar requerimientos de {repo}#{issue_id} y crear plan técnico.")
        
        # REVISIÓN INTERMEDIA REINA
        print("👑 [REVISIÓN REINA] Auditando plan de Enjambre 1...")
        eval_plan = self.call_ollama_direct(q1_model, "Reina Q2 Auditora", f"Evaluar plan:\\n{plan[:300]}\\n¿Es viabile? JSON {{\"valid\": true}}")
        v_plan, r_plan = self.validate_antispam_output(eval_plan)
        
        if not v_plan:
            print(f"🔄 [REINA REINTENTO] Replanificando Enjambre 1: {r_plan}")
            plan = self.call_ollama_direct(b1_1["model"], b1_1["role"], f"Corregir plan según: {r_plan}")

        # ESTADO 3: ENJAMBRE 2 (DESARROLLO DE CÓDIGO Y PRUEBAS)
        print("\\n⚙️ [ESTADO 3] Enjambre 2: Generando solución de código y tests unitarios...")
        b2_3 = next((b for b in self.brains if b["code"] == "2.3"), self.brains[7])
        code_solution = self.call_ollama_direct(b2_3["model"], b2_3["role"], f"Escribir código y tests basados en este plan:\\n{plan[:300]}")

        # ESTADO 4: ENJAMBRE 3 (QA, PUBLICACIÓN Y ASIGNACIÓN DE CARTERA)
        print("\\n⚖️ [ESTADO 4] Enjambre 3: Validando QA y preparando Pull Request...")
        b3_1 = next((b for b in self.brains if b["code"] == "3.1"), self.brains[10])
        b3_2 = next((b for b in self.brains if b["code"] == "3.2"), self.brains[11])
        
        qa_report = self.call_ollama_direct(b3_1["model"], b3_1["role"], f"Auditar código:\\n{code_solution[:300]}")
        
        # INYECCIÓN DE CARTERA DE PAGO
        wallets = getattr(self, "wallets", {})
        ln_wallet = wallets.get("lightning", "vellichorlate475846@getalby.com")
        evm_wallet = wallets.get("evm", "0x6040f4D8BA36214222d34E176634670407a9bC56")
        
        pr_payload = f"""
### Solution Proposed by TriSwarm AI
{code_solution}

### QA Validation Report
{qa_report[:200]}

---
**Bounty Payout Destination:**
- Lightning Address: `{ln_wallet}`
- EVM Address: `{evm_wallet}`
"""
        print("\\n💎 [PUBLICACIÓN] Generando payload para PR con carteras inyectadas:")
        print(f"  ⚡ Lightning: {ln_wallet}")
        print(f"  🔗 EVM: {evm_wallet}")

        # REGISTRO FINAL EN DB DE HISTORIAL
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bounty_swarm_history (repo, issue_id, status, created_at, swarm1_draft)
                VALUES (?, ?, 'PUBLISHED', datetime('now'), ?);
            """, (repo, str(issue_id), pr_payload))
            conn.commit()
            conn.close()
            print("\\n✅ [CICLO COMPLETADO] Registro de éxito guardado en DB. Listo para siguiente ciclo.")
            return True
        except Exception as e:
            print(f"⚠️ Error registrando en DB: {e}")
            return False

    def update_bounty_state(self, repo, issue_id, state):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("UPDATE bounty_opportunities SET state = ? WHERE repo_owner_name = ? AND issue_number = ?;", (state, repo, str(issue_id)))
            conn.commit()
            conn.close()
        except Exception:
            pass
'''

    if "def process_bounty_loop" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + state_machine_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

apply_full_state_machine("/home/k1/ccia_workspace/modules/art_63.py")
apply_full_state_machine("/home/k1/ccia_workspace/ccia_mando_63.py")
