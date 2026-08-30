# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_consensus_patch(code: str) -> str:
    old_opt3_pattern = 'res = refiner.run_refinement_loop(task)'
    
    new_opt3_injection = """res = refiner.run_refinement_loop(task)
                    try:
                        from multiagent_consensus_auditor import verify_consensus
                        consensus_ok, consensus_msg = verify_consensus(str(res))
                        console.print(f"🤝 [bold cyan]Auditoría de Consenso (DeepSeek-R1):[/bold cyan] {consensus_msg}")
                    except Exception:
                        pass"""

    if old_opt3_pattern in code and "multiagent_consensus_auditor" not in code:
        code = code.replace(old_opt3_pattern, new_opt3_injection, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_consensus_patch,
        module_name="multiagent_consensus_auditor",
        description="Auditoría de consenso cruzado entre modelos LLM en Opción 3"
    )
    sys.exit(0 if success else 1)
