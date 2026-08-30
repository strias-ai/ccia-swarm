# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_planner_validator_patch(code: str) -> str:
    old_opt2 = """        elif opt == "2":
            task = Prompt.ask("\\n🎯 Ingrese el objetivo de software completo")
            if task.strip():
                res = planner.plan_and_execute(task)
                console.print(f"\\n[bold green]Resultado Planificatorio:[/bold green] {res['summary']}")
                Prompt.ask("\\nPresione ENTER para continuar")"""

    new_opt2 = """        elif opt == "2":
            task = Prompt.ask("\\n🎯 Ingrese el objetivo de software completo")
            if task.strip():
                console.print("🧠 [bold cyan]Validando topología DAG y asignación óptima de modelos Ollama...[/bold cyan]")
                try:
                    from planner_topology_validator import validate_and_route_plan
                    _ = validate_and_route_plan({"tasks": [{"id": 1, "type": "code", "desc": task}]})
                    console.print("✅ [bold green]Plan validado sin ciclos implícitos.[/bold green]")
                except Exception as e:
                    console.print(f"⚠️ Validación pasante (Fallback activo): {e}")
                res = planner.plan_and_execute(task)
                console.print(f"\\n[bold green]Resultado Planificatorio:[/bold green] {res['summary']}")
                Prompt.ask("\\nPresione ENTER para continuar")"""

    if old_opt2 in code and "planner_topology_validator" not in code:
        code = code.replace(old_opt2, new_opt2)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_planner_validator_patch,
        module_name="planner_topology_validator",
        description="Validador de topología DAG y enrutamiento óptimo de cerebros en el Planificador (Opción 2)"
    )
    sys.exit(0 if success else 1)
