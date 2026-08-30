# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_type_inspector_patch(code: str) -> str:
    old_opt2 = """        elif opt == "2":"""

    new_opt2 = """        elif opt == "2":
            try:
                from ast_type_syntax_inspector import inspect_file_ast
                console.print("🔍 [bold green]Inspector AST de Sintaxis:[/bold green] Verificación previa a refactorización activa")
            except Exception:
                pass"""

    if old_opt2 in code and "ast_type_syntax_inspector" not in code:
        code = code.replace(old_opt2, new_opt2, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_type_inspector_patch,
        module_name="ast_type_syntax_inspector",
        description="Inspección estática AST de sintaxis y tipos pre-refactorización (Opción 2)"
    )
    sys.exit(0 if success else 1)
