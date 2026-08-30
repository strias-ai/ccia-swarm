# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_telemetry_exporter_patch(code: str) -> str:
    old_opt12 = """        elif opt == "12":"""

    new_opt12 = """        elif opt == "12":
            try:
                from system_health_telemetry_exporter import collect_telemetry_snapshot
                t_snap = collect_telemetry_snapshot()
                console.print(f"📊 [bold green]Telemetría Dashboard (Opción 12):[/bold green] CPU {t_snap['cpu_percent']}% | RAM {t_snap['ram_percent']}% | {t_snap['active_modules']} módulos activos [{t_snap['status']}]")
            except Exception:
                pass"""

    if old_opt12 in code and "system_health_telemetry_exporter" not in code:
        code = code.replace(old_opt12, new_opt12, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_telemetry_exporter_patch,
        module_name="system_health_telemetry_exporter",
        description="Exporter de telemetría y consolidación de salud del sistema (Opción 12)"
    )
    sys.exit(0 if success else 1)
