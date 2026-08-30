# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_hr_broker_patch(code: str) -> str:
    old = """        elif opt == "4":"""
    new = """        elif opt == "4":
            try:
                from human_resource_broker import list_pending_tickets
                tickets = list_pending_tickets()
                if tickets:
                    console.print(f"🎫 [bold yellow]Human Broker:[/bold yellow] {len(tickets)} ticket(s) pendiente(s) de aprobación humana")
            except Exception:
                pass"""
    if old in code and "human_resource_broker" not in code:
        return code.replace(old, new, 1)
    return code

compiler = CCIACompiler()
p1 = compiler.compile_patch(apply_hr_broker_patch, "human_resource_broker", "Broker de Solicitudes Recursos Humano-Agente (Opción 4)")
sys.exit(0 if p1 else 1)
