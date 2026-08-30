# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_mock_fixture_patch(code: str) -> str:
    old_opt9 = """        elif opt == "9":"""

    new_opt9 = """        elif opt == "9":
            try:
                from mock_data_fixture_generator import generate_user_payload
                payload = generate_user_payload()
                console.print(f"🧪 [bold cyan]Generador de Mocks/Fixtures:[/bold cyan] Payload sintético listo [{payload['username']}]")
            except Exception:
                pass"""

    if old_opt9 in code and "mock_data_fixture_generator" not in code:
        code = code.replace(old_opt9, new_opt9, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_mock_fixture_patch,
        module_name="mock_data_fixture_generator",
        description="Generación de fixtures y payloads sintéticos para suites de prueba (Opción 9)"
    )
    sys.exit(0 if success else 1)
