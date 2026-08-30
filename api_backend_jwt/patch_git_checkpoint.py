# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_git_checkpoint_patch(code: str) -> str:
    old_opt10 = """        elif opt == "10":"""

    new_opt10 = """        elif opt == "10":
            try:
                from git_auto_checkpoint import create_git_checkpoint
                create_git_checkpoint("manual_opt10_backup")
                console.print("📦 [bold green]Git Checkpoint:[/bold green] Micro-commit de estado registrado.")
            except Exception:
                pass"""

    if old_opt10 in code and "git_auto_checkpoint" not in code:
        code = code.replace(old_opt10, new_opt10, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_git_checkpoint_patch,
        module_name="git_auto_checkpoint",
        description="Motor de micro-commits automáticos en Git para el Workspace (Opción 10)"
    )
    sys.exit(0 if success else 1)
