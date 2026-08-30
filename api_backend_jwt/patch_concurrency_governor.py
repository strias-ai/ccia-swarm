# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_concurrency_governor_patch(code: str) -> str:
    old_opt4 = """        elif opt == "4":"""

    new_opt4 = """        elif opt == "4":
            try:
                from thread_concurrency_governor import get_optimal_thread_limit
                lim = get_optimal_thread_limit()
                console.print(f"⚡ [bold cyan]Gobernador de Concurrencia (Opción 4):[/bold cyan] Máximo {lim} hilos activos")
            except Exception:
                pass"""

    if old_opt4 in code and "thread_concurrency_governor" not in code:
        code = code.replace(old_opt4, new_opt4, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_concurrency_governor_patch,
        module_name="thread_concurrency_governor",
        description="Gobernador de hilos dinámicos según carga de CPU en la Opción 4"
    )
    sys.exit(0 if success else 1)
