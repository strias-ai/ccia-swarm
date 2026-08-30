# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_integrity_sentinel_patch(code: str) -> str:
    old_opt11 = """        elif opt == "11":"""

    new_opt11 = """        elif opt == "11":
            try:
                from module_integrity_sentinel import verify_registered_modules
                s_res = verify_registered_modules()
                console.print(f"🛡️ [bold green]Sentinel de Integridad Artefactos:[/bold green] {s_res['verified_count']} módulos verificados ({s_res['status']})")
            except Exception:
                pass"""

    if old_opt11 in code and "module_integrity_sentinel" not in code:
        code = code.replace(old_opt11, new_opt11, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_integrity_sentinel_patch,
        module_name="module_integrity_sentinel",
        description="Verificación de firmas e integridad de código fuente de artefactos (Opción 11)"
    )
    sys.exit(0 if success else 1)
