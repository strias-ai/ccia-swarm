# -*- coding: utf-8 -*-
"""
CCIA OPENAPI SPEC GENERATOR v1.0
Genera esquemas OpenAPI v3.0 dinámicos inspeccionando las rutas del backend en la Opción 3.
"""
import json
import os
import re

def generate_openapi_schema(backend_file: str = "main.py") -> dict:
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "CCIA API Spec",
            "version": "1.0.0",
            "description": "Especificación de endpoints autogenerada por CCIA Agent Engine"
        },
        "paths": {}
    }
    
    target_path = os.path.join(os.path.dirname(__file__), backend_file)
    if not os.path.exists(target_path):
        return schema

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        routes = re.findall(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', content)
        for method, path in routes:
            if path not in schema["paths"]:
                schema["paths"][path] = {}
            schema["paths"][path][method.lower()] = {
                "summary": f"Endpoint {method.upper()} {path}",
                "responses": {"200": {"description": "Respuesta exitosa"}}
            }
    except Exception:
        pass
        
    return schema

if __name__ == "__main__":
    spec = generate_openapi_schema()
    print(f"📄 Especificación OpenAPI: {len(spec['paths'])} rutas detectadas")
