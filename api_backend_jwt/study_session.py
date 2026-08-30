# -*- coding: utf-8 -*-
import urllib.request
import json
import random
from university_dean import UniversityDean

AGENTS_MAP = {
    "scout_lib": "Exploración de Librerías",
    "builder": "Arquitectura y FastAPI",
    "evaluator": "Seguridad y Calidad",
    "cleaner": "Refactorización y Rendimiento",
    "grower": "Modelos Inteligentes y LLMs"
}

REPOSITORIES = [
    {"topic": "FastAPI Web Framework", "url": "https://api.github.com/repos/tiangolo/fastapi"},
    {"topic": "SQLAlchemy ORM 2.0", "url": "https://api.github.com/repos/sqlalchemy/sqlalchemy"},
    {"topic": "Python Security Audit (Bandit)", "url": "https://api.github.com/repos/PyCQA/bandit"},
    {"topic": "LangChain Framework", "url": "https://api.github.com/repos/langchain-ai/langchain"},
    {"topic": "Ollama Local Engine", "url": "https://api.github.com/repos/ollama/ollama"},
    {"topic": "Rich Console Toolkit", "url": "https://api.github.com/repos/Textualize/rich"}
]

def run_immediate_study():
    print("\n==========================================================")
    print(" 🎓 SESIÓN EN VIVO: APRENDIZAJE AUTÓNOMO E INGRESO EN MEMORIA")
    print("==========================================================\n")
    dean = UniversityDean()
    
    for agent, specialty in AGENTS_MAP.items():
        target = random.choice(REPOSITORIES)
        print(f"🤖 [{agent.upper()}] (Especialidad: {specialty})")
        print(f"   ├─ Accediendo a repositorio libre: {target['topic']}")
        
        try:
            req = urllib.request.Request(target["url"], headers={'User-Agent': 'CCIA-University-Agent'})
            with urllib.request.urlopen(req, timeout=4) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode())
                    desc = data.get("description") or "Documentación técnica abierta"
                    stars = data.get("stargazers_count", 0)
                    summary = f"{target['topic']}: {desc} (Popularidad: {stars} estrellas)."
                    
                    msg = dean.submit_research(agent, target["topic"], target["url"], summary)
                    print(f"   └─ {msg}\n")
        except Exception as e:
            print(f"   └─ [Error de conexión]: {e}\n")

    print("🧑‍🏫 [DECANO AI] Evaluando investigaciones y actualizando niveles de memoria...")
    grades = dean.evaluate_and_grade()
    for g in grades:
        print(f"   ├─ Tesis #{g['id']} de {g['agent']} ({g['topic']}): Status -> {g['status']}")
    print("\n==========================================================\n")

if __name__ == "__main__":
    run_immediate_study()


# Alias para compatibilidad
run_autonomous_study_hour = run_immediate_study
