# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_gc_reclaimer_patch(code: str) -> str:
    old_opt10 = """        elif opt == "10":"""

    new_opt10 = """        elif opt == "10":
            try:
                from gc_memory_reclaimer import reclaim_system_memory
                stats = reclaim_system_memory()
                console.print(f"🧹 [bold green]Purga de Memoria RAM/VRAM:[/bold green] Liberados {stats['unreachable_objects_freed']} objetos huérfanos")
            except Exception:
                pass"""

    if old_opt10 in code and "gc_memory_reclaimer" not in code:
        code = code.replace(old_opt10, new_opt10, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_gc_reclaimer_patch,
        module_name="gc_memory_reclaimer",
        description="Purga forzada de objetos en memoria RAM/VRAM y compactación de malloc (Opción 10)"
    )
    sys.exit(0 if success else 1)
