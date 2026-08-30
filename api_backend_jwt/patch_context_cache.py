# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_context_cache_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":"""

    new_opt8 = """        elif opt == "8":
            try:
                from ollama_context_cache import get_prompt_hash
                h = get_prompt_hash("opt8_ping")
                console.print(f"⚡ [bold cyan]Cache Contextual Ollama:[/bold cyan] Hash Engine Activo [{h[:8]}]")
            except Exception:
                pass"""

    if old_opt8 in code and "ollama_context_cache" not in code:
        code = code.replace(old_opt8, new_opt8, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_context_cache_patch,
        module_name="ollama_context_cache",
        description="Reutilización de cache contextual de prompts para Ollama en la Opción 8"
    )
    sys.exit(0 if success else 1)
