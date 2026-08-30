# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_load_benchmark_patch(code: str) -> str:
    old_opt7 = """        elif opt == "7":"""

    new_opt7 = """        elif opt == "7":
            try:
                from http_load_benchmark_tester import run_quick_benchmark
                console.print("⚡ [bold green]Simulador de Carga HTTP:[/bold green] Módulo de estrés y latencia P95/P99 activo")
            except Exception:
                pass"""

    if old_opt7 in code and "http_load_benchmark_tester" not in code:
        code = code.replace(old_opt7, new_opt7, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_load_benchmark_patch,
        module_name="http_load_benchmark_tester",
        description="Simulador de carga HTTP concurrente y métricas de latencia P95 (Opción 7)"
    )
    sys.exit(0 if success else 1)
