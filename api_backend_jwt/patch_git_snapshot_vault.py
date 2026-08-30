# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_git_snapshot_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":"""

    new_opt8 = """        elif opt == "8":
            try:
                from git_auto_snapshot_vault import create_git_snapshot
                snap = create_git_snapshot("Check-in desde panel principal Opción 8")
                console.print(f"📦 [bold cyan]Bóveda Git de Snapshots:[/bold cyan] Estado={snap['status']} ({snap['msg']})")
            except Exception:
                pass"""

    if old_opt8 in code and "git_auto_snapshot_vault" not in code:
        code = code.replace(old_opt8, new_opt8, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_git_snapshot_patch,
        module_name="git_auto_snapshot_vault",
        description="Gestión de checkpoints automáticos y puntos de reversión Git (Opción 8)"
    )
    sys.exit(0 if success else 1)
