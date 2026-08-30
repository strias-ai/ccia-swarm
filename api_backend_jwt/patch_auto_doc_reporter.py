# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_auto_doc_patch(code: str) -> str:
    old_opt11 = """        elif opt == "11":"""

    new_opt11 = """        elif opt == "11":
            try:
                from auto_doc_reporter import generate_system_report
                console.print(f"\\n[bold green]{generate_system_report()}[/bold green]")
            except Exception:
                pass"""

    if old_opt11 in code and "auto_doc_reporter" not in code:
        code = code.replace(old_opt11, new_opt11, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_auto_doc_patch,
        module_name="auto_doc_reporter",
        description="Generador automático de documentación e informes de arquitectura (Opción 11)"
    )
    sys.exit(0 if success else 1)
