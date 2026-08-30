# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_websocket_streamer_patch(code: str) -> str:
    old_opt7 = """        elif opt == "7":"""

    new_opt7 = """        elif opt == "7":
            try:
                from websocket_event_streamer import broadcast_event
                broadcast_event("TELEMETRY_REFRESH", {"source": "CLI_OPT7"})
                console.print("📡 [bold green]Canal WebSocket de Telemetría:[/bold green] Sincronizado con :8090")
            except Exception:
                pass"""

    if old_opt7 in code and "websocket_event_streamer" not in code:
        code = code.replace(old_opt7, new_opt7, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_websocket_streamer_patch,
        module_name="websocket_event_streamer",
        description="Emisión de eventos en tiempo real hacia el Dashboard Web (Opción 7)"
    )
    sys.exit(0 if success else 1)
