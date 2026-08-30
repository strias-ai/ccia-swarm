# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_thesis_defense_patch(code: str) -> str:
    old_opt5 = """        elif opt == "5":"""

    new_opt5 = """        elif opt == "5":
            try:
                from thesis_auto_defense import evaluate_and_promote_agents
                promo_msg = evaluate_and_promote_agents()
                console.print(f"\\n🎓 [bold yellow]Evaluación de Tesis y Ascensos:[/bold yellow]\\n{promo_msg}")
            except Exception:
                pass"""

    if old_opt5 in code and "thesis_auto_defense" not in code:
        code = code.replace(old_opt5, new_opt5, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_thesis_defense_patch,
        module_name="thesis_auto_defense",
        description="Defensa de Tesis y ascenso automático de nivel en el Skill Tree (Opción 5)"
    )
    sys.exit(0 if success else 1)
