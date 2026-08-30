# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_watchdog_patch(code: str) -> str:
    old_opt11 = """        elif opt == "11":
            console.print("\\n🛡️ [bold magenta]Auditoría de Integridad CCIA:[/bold magenta]")"""

    new_opt11 = """        elif opt == "11":
            import subprocess
            subprocess.run(["python3", "/home/k1/ccia_workspace/api_backend_jwt/self_healing_watchdog.py", "--single"])
            console.print("\\n🛡️ [bold magenta]Auditoría de Integridad CCIA:[/bold magenta]")"""

    if old_opt11 in code and "self_healing_watchdog.py" not in code:
        code = code.replace(old_opt11, new_opt11)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_watchdog_patch,
        module_name="self_healing_watchdog",
        description="Daemon de autocuración activa para Dashboard (8090) e integridad SQLite (Opción 11)"
    )
    sys.exit(0 if success else 1)
