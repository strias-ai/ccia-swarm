# -*- coding: utf-8 -*-
"""
CCIA v14.0 - Matrix de Capacidades y Necesidades de Optimización por Agente
Hardware: NucBox-K11 (AMD Radeon 780M APU)
"""

CCIA_FLEET = {
    "project": {
        "nombre": "Project-Builder",
        "cerebro": "qwen2.5-coder:3b",
        "rol": "Scaffolding de proyectos multi-archivo",
        "capacidades": ["Generación de árbol de archivos", "Proyección de arquitecturas modularizadas", "Sanitización de nombres de rutas"],
        "necesidades_mejora": ["Equilibrio de dependencias en requirements.txt", "Definición estricta de imports relativos"]
    },
    "planner": {
        "nombre": "Planificador-AI",
        "cerebro": "qwen2.5-coder:3b",
        "rol": "Descomposición JSON de tareas complejas",
        "capacidades": ["Análisis de ambigüedad interactiva", "Generación de esquemas JSON estructurados"],
        "necesidades_mejora": ["Reducción de latencia en análisis de requisitos", "Validador JSON con fallback automático"]
    },
    "builder": {
        "nombre": "Constructor-AI",
        "cerebro": "qwen2.5-coder:3b",
        "rol": "Infraestructura y Código Producción",
        "capacidades": ["Escritura de código Python 100% no interactivo", "Integración con módulos CCIA"],
        "necesidades_mejora": ["Filtrado estricto de textos/prosa en salida del LLM", "Manejo explícito de excepciones"]
    },
    "evaluator": {
        "nombre": "Auditor-AI",
        "cerebro": "deepseek-r1:1.5b",
        "rol": "Evaluación de Calidad y Seguridad",
        "capacidades": ["Análisis estático de sintaxis AST", "Sandboxing y prevención de exec() inseguro"],
        "necesidades_mejora": ["Reglas linter avanzadas (PEP8/Flake8)", "Análisis de vectores de inyección en CLI"]
    },
    "cleaner": {
        "nombre": "Limpiador-AI",
        "cerebro": "llama3.2:latest",
        "rol": "Refactorización y Rendimiento",
        "capacidades": ["Optimización de complejidad ciclomática", "Eliminación de código muerto"],
        "necesidades_mejora": ["Inlining de funciones cortas", "Optimización del uso de memoria RAM/VRAM"]
    },
    "grower": {
        "nombre": "Crecedor-AI",
        "cerebro": "llama3.2:latest",
        "rol": "Adaptación y Métricas de Escala",
        "capacidades": ["Evaluación de telemetría hardware", "Ajuste dinámico de context-window"],
        "necesidades_mejora": ["Métricas en tiempo real de FPS/Tokens por segundo en Radeon 780M"]
    },
    "maintainer": {
        "nombre": "Mantenedor-AI",
        "cerebro": "llama3.2:latest",
        "rol": "Daemon Auditor y Seguridad DB",
        "capacidades": ["Gestión de cola SQLite de buzón", "Purgado e integridad de registros temporales"],
        "necesidades_mejora": ["Autoreparación de corrupciones de base de datos", "Indexación periódica"]
    },
    "scout_lib": {
        "nombre": "Scout & Librarian",
        "cerebro": "gemma2:2b / DB",
        "rol": "Exploración RAG e Indexación DB",
        "capacidades": ["Búsqueda vectorial en Skill Tree", "Indexación RAG de documentos aprobados"],
        "necesidades_mejora": ["Chunking adaptativo por tamaño de archivo", "Ranking semántico mejorado"]
    }
}

def analizar_flota():
    print("=" * 75)
    print("🛸 DIAGNÓSTICO DE CAPACIDADES Y OPORTUNIDADES DE MEJORA - FLOTA CCIA v14.0")
    print("=" * 75)
    for agent_id, data in CCIA_FLEET.items():
        print(f"🤖 AGENTE [{agent_id.upper()}] - {data['nombre']} ({data['cerebro']})")
        print(f"   📌 Rol: {data['rol']}")
        print("   ✅ Capacidades Actuales:")
        for cap in data['capacidades']:
            print(f"      • {cap}")
        print("   💡 Necesidades para Ser Mejor:")
        for nec in data['necesidades_mejora']:
            print(f"      👉 {nec}")
        print("-" * 75)

if __name__ == "__main__":
    analizar_flota()
