# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_secrets_vault_patch(code: str) -> str:
    old_opt11 = """        elif opt == "11":"""

    new_opt11 = """        elif opt == "11":
            try:
                from env_secrets_vault import audit_environment_secrets
                v_res = audit_environment_secrets()
                console.print(f"🔒 [bold cyan]Bóveda de Secretos .env:[/bold cyan] {len(v_res)} variables auditadas")
            except Exception:
                pass"""

    if old_opt11 in code and "env_secrets_vault" not in code:
        code = code.replace(old_opt11, new_opt11, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_secrets_vault_patch,
        module_name="env_secrets_vault",
        description="Auditoría y enmascaramiento seguro de variables de entorno y secretos (Opción 11)"
    )
    sys.exit(0 if success else 1)
