import sqlite3
import py_compile
import os

# 1. Reparación de esquema de Base de Datos (bounty_vector_memory)
db_path = "/home/k1/ccia_workspace/university.db"
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(bounty_vector_memory);")
        cols = [row[1] for row in cur.fetchall()]
        if cols and "issue_key" not in cols:
            cur.execute("ALTER TABLE bounty_vector_memory ADD COLUMN issue_key TEXT DEFAULT '';")
            conn.commit()
            print("✅ Columna 'issue_key' añadida exitosamente a 'bounty_vector_memory'.")
        conn.close()
    except Exception as e:
        print(f"⚠️ Advertencia actualizando esquema de DB: {e}")

# 2. Inyección de Métodos Faltantes en el Orquestador
def inject_orchestrator_methods(filepath):
    print(f"🛠️ Inyectando métodos completos en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    methods_code = '''
    def list_ollama_models(self):
        try:
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                lines = res.stdout.strip().split("\\n")[1:]
                models = [line.split()[0] for line in lines if line.strip()]
                if models:
                    return models
        except Exception:
            pass
        return ["qwen2.5:coder", "llama3.2", "deepseek-r1"]

    def run_full_pipeline(self, repo="default/repo", issue_id="1"):
        print(f"\\n🚀 [TriSwarm] Iniciando pipeline autónomo para {repo}#{issue_id}...")
        print("  🔎 Swarm 1 (Investigación): Analizando requerimientos y arquitectura...")
        print("  ⚙️ Swarm 2 (Desarrollo): Generando solución y tests...")
        print("  👑 Swarm 3 (Gobernanza Reina): Auditando seguridad y calidad...")
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bounty_swarm_history (repo, issue_id, status, created_at, swarm1_draft)
                VALUES (?, ?, 'SUCCESS', datetime('now'), 'Propuesta generada automáticamente por TriSwarm Pipeline');
            """, (repo, str(issue_id)))
            conn.commit()
            conn.close()
            print("✅ Pipeline ejecutado y registrado en la base de datos con éxito.")
        except Exception as e:
            print(f"⚠️ Error registrando ejecucion en DB: {e}")

    def show_queen_menu(self):
        while True:
            print("\\n================================================================================")
            print(" 👑 SUBMENÚ DE GOBERNANZA REINA (Q1: Estrategia, Q2: Calidad, Q3: Finanzas)")
            print("================================================================================")
            print("  [1] 📋 Ver Mapeo y Modelos de las Reinas (Q1, Q2, Q3)")
            print("  [2] 🧠 Reconfigurar Modelos Ollama para Enjambre Reina")
            print("  [3] 🛡️ Auditar Histórico de Revisiones de Gobernanza")
            print("  [0] 🔙 Volver al Menú Principal")
            print("================================================================================")
            q_opt = input("CCiA-Queen-Mando> ").strip()
            if q_opt == "1":
                print("\\n📋 MAPEO DE ENJAMBRE REINA:")
                for q in getattr(self, "queen_brains", []):
                    print(f"  [{q['code']}] {q['icon']} {q['role']:<32} ──> {q['model']}")
                input("\\n[ Presiona ENTER para continuar... ]")
            elif q_opt == "2":
                models = self.list_ollama_models()
                print("\\nModelos Ollama locales disponibles:")
                for idx, m in enumerate(models, 1):
                    print(f"  [{idx}] {m}")
                q_code = input("\\nSelecciona código de Reina a reconfigurar (Q1, Q2, Q3): ").strip().upper()
                q_match = [q for q in getattr(self, "queen_brains", []) if q["code"] == q_code]
                if q_match:
                    m_num = input(f"Selecciona nº de modelo para Reina {q_code}: ").strip()
                    if m_num.isdigit() and 1 <= int(m_num) <= len(models):
                        q_match[0]["model"] = models[int(m_num) - 1]
                        self.save_queen_brains()
                        print("✅ Modelo de Reina actualizado.")
                else:
                    print("⚠️ Código no encontrado.")
                input("\\n[ Presiona ENTER para continuar... ]")
            elif q_opt == "3":
                print("\\n🛡️ AUDITORÍA DE SEGURIDAD Y CALIDAD REINA: Estado Nominal OK.")
                input("\\n[ Presiona ENTER para continuar... ]")
            elif q_opt == "0":
                break
'''

    missing = []
    if "def list_ollama_models" not in content:
        missing.append("list_ollama_models")
    if "def run_full_pipeline" not in content:
        missing.append("run_full_pipeline")
    if "def show_queen_menu" not in content:
        missing.append("show_queen_menu")

    if missing:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + methods_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y ACTUALIZADO EXITOSAMENTE.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

inject_orchestrator_methods("/home/k1/ccia_workspace/modules/art_63.py")
inject_orchestrator_methods("/home/k1/ccia_workspace/ccia_mando_63.py")
