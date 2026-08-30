# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_wal_optimizer_patch(code: str) -> str:
    old_opt11 = """        elif opt == "11":"""

    new_opt11 = """        elif opt == "11":
            try:
                from sqlite_wal_optimizer import optimize_database_concurrency
                wal_status = optimize_database_concurrency()
                console.print(f"🗄️ [bold cyan]Salud DB Concurrente:[/bold cyan] {wal_status}")
            except Exception:
                pass"""

    if old_opt11 in code and "sqlite_wal_optimizer" not in code:
        code = code.replace(old_opt11, new_opt11, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_wal_optimizer_patch,
        module_name="sqlite_wal_optimizer",
        description="Optimizador de concurrencia SQLite WAL e índices de base de datos (Opción 11)"
    )
    sys.exit(0 if success else 1)
