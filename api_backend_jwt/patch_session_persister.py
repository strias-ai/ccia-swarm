# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_session_persister_patch(code: str) -> str:
    old_opt12 = """        elif opt == "12":"""

    new_opt12 = """        elif opt == "12":
            try:
                from session_state_persister import persist_session_and_shutdown
                console.print(f"\\n[bold green]{persist_session_and_shutdown()}[/bold green]")
            except Exception:
                pass"""

    if old_opt12 in code and "session_state_persister" not in code:
        code = code.replace(old_opt12, new_opt12, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_session_persister_patch,
        module_name="session_state_persister",
        description="Persistencia de estado de sesión y apagado elegante en la Opción 12"
    )
    sys.exit(0 if success else 1)
