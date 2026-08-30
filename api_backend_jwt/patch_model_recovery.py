# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_model_recovery_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":"""

    new_opt8 = """        elif opt == "8":
            try:
                from ollama_model_auto_recovery import audit_and_preload_models
                res = audit_and_preload_models()
                console.print(f"🤖 [bold green]Disponibilidad LLM Local:[/bold green] {res}")
            except Exception:
                pass"""

    if old_opt8 in code and "ollama_model_auto_recovery" not in code:
        code = code.replace(old_opt8, new_opt8, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_model_recovery_patch,
        module_name="ollama_model_auto_recovery",
        description="Verificación de disponibilidad y precarga de modelos Ollama (Opción 8)"
    )
    sys.exit(0 if success else 1)
