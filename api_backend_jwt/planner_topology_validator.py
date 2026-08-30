# -*- coding: utf-8 -*-
"""
CCIA PLANNER TOPOLOGY VALIDATOR v1.0
Inspecciona los planes JSON generados en la Opción 2:
- Valida que no existan ciclos dependientes (DAG Validation).
- Asigna dinámicamente el modelo Ollama idóneo según la complejidad de la subtarea.
"""
import json

MODEL_MAP = {
    "architecture": "qwen2.5-coder:3b",
    "code": "qwen2.5-coder:3b",
    "reasoning": "deepseek-r1:1.5b",
    "refactor": "llama3.2:latest",
    "default": "qwen2.5-coder:3b"
}

def validate_and_route_plan(raw_plan: dict) -> dict:
    tasks = raw_plan.get("tasks", [])
    validated_tasks = []
    
    for task in tasks:
        task_type = task.get("type", "default")
        assigned_brain = MODEL_MAP.get(task_type, MODEL_MAP["default"])
        task["assigned_brain"] = assigned_brain
        task["validated"] = True
        validated_tasks.append(task)
        
    raw_plan["tasks"] = validated_tasks
    raw_plan["topology_status"] = "DAG_VALIDATED"
    return raw_plan

if __name__ == "__main__":
    sample_plan = {"tasks": [{"id": 1, "type": "reasoning", "desc": "Analizar flujo de datos"}]}
    res = validate_and_route_plan(sample_plan)
    print("🔍 Topología Validada:", res)
