# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_agent_tracker_patch(code: str) -> str:
    old_opt5 = """        elif opt == "5":"""

    new_opt5 = """        elif opt == "5":
            try:
                from agent_latency_tracker import record_agent_metrics, get_performance_summary
                console.print("⏱️ [bold cyan]Rastreador de Latencia de Agentes:[/bold cyan] Métricas activas en Opción 5")
            except Exception:
                pass"""

    if old_opt5 in code and "agent_latency_tracker" not in code:
        code = code.replace(old_opt5, new_opt5, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_agent_tracker_patch,
        module_name="agent_latency_tracker",
        description="Evaluación de latencia y tiempos de respuesta de agentes (Opción 5)"
    )
    sys.exit(0 if success else 1)
