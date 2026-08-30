# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_prompt_tuner_patch(code: str) -> str:
    old_opt5 = """        elif opt == "5":"""

    new_opt5 = """        elif opt == "5":
            try:
                from agent_prompt_tuner import tune_all_agents
                tune_all_agents()
            except Exception:
                pass"""

    if old_opt5 in code and "agent_prompt_tuner" not in code:
        code = code.replace(old_opt5, new_opt5, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_prompt_tuner_patch,
        module_name="agent_prompt_tuner",
        description="Ajuste automático de System Prompts basado en autopsias de error (Opción 5)"
    )
    sys.exit(0 if success else 1)
