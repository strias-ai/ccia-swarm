# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_vram_profiler_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":"""

    new_opt8 = """        elif opt == "8":
            try:
                from inference_vram_profiler import VRAMProfiler
                profiler = VRAMProfiler()
                console.print("📊 [bold green]Profiler de VRAM/Inferencia:[/bold green] Medición de tok/s activa")
            except Exception:
                pass"""

    if old_opt8 in code and "inference_vram_profiler" not in code:
        code = code.replace(old_opt8, new_opt8, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_vram_profiler_patch,
        module_name="inference_vram_profiler",
        description="Profiler de métricas de rendimiento (tokens/seg) y VRAM (Opción 8)"
    )
    sys.exit(0 if success else 1)
