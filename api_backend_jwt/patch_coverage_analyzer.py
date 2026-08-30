# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_coverage_analyzer_patch(code: str) -> str:
    old_opt9 = """        elif opt == "9":"""

    new_opt9 = """        elif opt == "9":
            try:
                from pytest_coverage_analyzer import analyze_workspace_coverage
                metrics = analyze_workspace_coverage()
                console.print(f"🧪 [bold green]Métricas de Pruebas Pytest:[/bold green] {metrics['test_files']} tests para {metrics['code_files']} archivos ({metrics['coverage_index']}% cobertura estim.)")
            except Exception:
                pass"""

    if old_opt9 in code and "pytest_coverage_analyzer" not in code:
        code = code.replace(old_opt9, new_opt9, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_coverage_analyzer_patch,
        module_name="pytest_coverage_analyzer",
        description="Analizador de cobertura de pruebas y densidad de aserciones Pytest (Opción 9)"
    )
    sys.exit(0 if success else 1)
