# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_dependency_graph_patch(code: str) -> str:
    old_opt6 = """        elif opt == "6":"""

    new_opt6 = """        elif opt == "6":
            try:
                from ast_dependency_graph_builder import build_dependency_graph
                dep_res = build_dependency_graph()
                console.print(f"🕸️ [bold green]Mapeador de Dependencias AST:[/bold green] {dep_res['total_modules']} módulos indexados")
            except Exception:
                pass"""

    if old_opt6 in code and "ast_dependency_graph_builder" not in code:
        code = code.replace(old_opt6, new_opt6, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_dependency_graph_patch,
        module_name="ast_dependency_graph_builder",
        description="Generación de mapa de importaciones y grafo de dependencias AST (Opción 6)"
    )
    sys.exit(0 if success else 1)
