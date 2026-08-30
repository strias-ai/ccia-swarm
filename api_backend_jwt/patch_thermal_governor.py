# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_thermal_patch(code: str) -> str:
    old_opt7 = """        elif opt == "7":"""

    new_opt7 = """        elif opt == "7":
            try:
                from apu_thermal_governor import audit_and_cool_down
                _, current_temp = audit_and_cool_down()
                console.print(f"🌡️ [bold cyan]Temperatura SoC APU AMD:[/bold cyan] {current_temp:.1f}°C")
            except Exception:
                pass"""

    if old_opt7 in code and "apu_thermal_governor" not in code:
        code = code.replace(old_opt7, new_opt7, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_thermal_patch,
        module_name="apu_thermal_governor",
        description="Gobernador térmico y protección del SoC Ryzen/Radeon en la Opción 7"
    )
    sys.exit(0 if success else 1)
