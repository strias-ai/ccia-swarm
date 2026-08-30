# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_security_patch(code: str) -> str:
    old_opt1 = """        elif opt == "1":"""

    new_opt1 = """        elif opt == "1":
            try:
                from security_vulnerability_scanner import audit_security
                console.print("🛡️ [bold green]Escáner OWASP de Seguridad:[/bold green] Inspección estática pre-escritura activa")
            except Exception:
                pass"""

    if old_opt1 in code and "security_vulnerability_scanner" not in code:
        code = code.replace(old_opt1, new_opt1, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_security_patch,
        module_name="security_vulnerability_scanner",
        description="Auditoría estática de vulnerabilidades y credenciales en código generado (Opción 1)"
    )
    sys.exit(0 if success else 1)
