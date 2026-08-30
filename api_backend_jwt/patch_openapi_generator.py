# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_openapi_generator_patch(code: str) -> str:
    old_opt3 = """        elif opt == "3":"""

    new_opt3 = """        elif opt == "3":
            try:
                from openapi_spec_generator import generate_openapi_schema
                schema = generate_openapi_schema()
                console.print(f"📄 [bold green]Generador OpenAPI v3.0:[/bold green] Esquema compilado con {len(schema['paths'])} rutas")
            except Exception:
                pass"""

    if old_opt3 in code and "openapi_spec_generator" not in code:
        code = code.replace(old_opt3, new_opt3, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_openapi_generator_patch,
        module_name="openapi_spec_generator",
        description="Generador automático de contratos y esquema OpenAPI v3.0 (Opción 3)"
    )
    sys.exit(0 if success else 1)
