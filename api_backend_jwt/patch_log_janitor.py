# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_log_janitor_patch(code: str) -> str:
    old_opt10 = """        elif opt == "10":"""

    new_opt10 = """        elif opt == "10":
            try:
                from log_rotation_janitor import cleanup_old_logs
                res = cleanup_old_logs()
                console.print(f"🧹 [bold cyan]Rotación de Logs:[/bold cyan] {res['logs_rotated']} procesados ({res['space_saved_mb']} MB liberados)")
            except Exception:
                pass"""

    if old_opt10 in code and "log_rotation_janitor" not in code:
        code = code.replace(old_opt10, new_opt10, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_log_janitor_patch,
        module_name="log_rotation_janitor",
        description="Rotación y purga automática de archivos de log en Opción 10"
    )
    sys.exit(0 if success else 1)
