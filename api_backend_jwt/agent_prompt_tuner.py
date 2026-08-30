# -*- coding: utf-8 -*-
"""
CCIA AGENT PROMPT TUNER v1.0
Lee autopsias de error y experimentos del Sandbox para ajustar dinámicamente
las directivas en el System Prompt de cada agente antes de ejecutar tareas.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

def generate_optimized_agent_directive(agent_id: str) -> str:
    """Genera reglas preventivas basadas en los fallos recientes del agente."""
    if not os.path.exists(DB_PATH):
        return ""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extraer errores recientes
    cursor.execute(
        "SELECT module, error_msg FROM error_autopsies WHERE agent_id = ? ORDER BY id DESC LIMIT 3",
        (agent_id,)
    )
    errors = cursor.fetchall()
    conn.close()

    if not errors:
        return f" Directiva {agent_id.upper()}: Mantener ejecución bajo estándares nominales."

    directives = [f"⚠️ DIRECTIVAS CORRECTIVAS OBLIGATORIAS PARA {agent_id.upper()}:"]
    for mod, msg in errors:
        directives.append(f"  • EVITAR FALLO EN [{mod}]: Prevenir '{msg[:80]}'")
    
    return "\n".join(directives)

def tune_all_agents():
    agents = ["project", "planner", "builder", "evaluator", "cleaner", "grower", "maintainer", "scout_lib"]
    print("🧠 [PROMPT TUNER] Optimizando directivas según historial de autopsias...")
    for ag in agents:
        directive = generate_optimized_agent_directive(ag)
        if "EVITAR FALLO" in directive:
            print(f"  • {ag}: Directiva de seguridad generada.")

if __name__ == "__main__":
    tune_all_agents()
