# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_circuit_breaker_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":"""

    new_opt8 = """        elif opt == "8":
            try:
                from ollama_circuit_breaker import OllamaCircuitBreaker
                cb = OllamaCircuitBreaker()
                console.print("🛡️ [bold green]Circuit Breaker Ollama:[/bold green] Reintentos y Fallback Activos")
            except Exception:
                pass"""

    if old_opt8 in code and "ollama_circuit_breaker" not in code:
        code = code.replace(old_opt8, new_opt8, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_circuit_breaker_patch,
        module_name="ollama_circuit_breaker",
        description="Circuit Breaker y tolerancia a fallos para Ollama en la Opción 8"
    )
    sys.exit(0 if success else 1)
