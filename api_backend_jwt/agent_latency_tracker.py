# -*- coding: utf-8 -*-
"""
CCIA AGENT LATENCY & PERFORMANCE TRACKER v1.0
Mide latencia por agente y genera estadísticas de respuesta en Opción 5.
"""
import time

_METRICS = {}

def record_agent_metrics(agent_role: str, elapsed_sec: float):
    if agent_role not in _METRICS:
        _METRICS[agent_role] = []
    _METRICS[agent_role].append(elapsed_sec)

def get_performance_summary() -> dict:
    summary = {}
    for role, times in _METRICS.items():
        if times:
            summary[role] = {
                "avg_sec": round(sum(times) / len(times), 2),
                "total_calls": len(times)
            }
    return summary

if __name__ == "__main__":
    record_agent_metrics("Builder", 1.25)
    record_agent_metrics("Evaluator", 0.85)
    print(f"⏱️ Métrica de Agentes: {get_performance_summary()}")
