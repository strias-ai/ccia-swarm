# -*- coding: utf-8 -*-
"""
CCIA AST TYPE & SYNTAX INSPECTOR v1.0
Valida la sintaxis y estructura sintáctica previo a refactorizaciones en la Opción 2.
"""
import ast
import os

def inspect_file_ast(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"status": "ERROR", "msg": "Archivo no encontrado"}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        
        return {
            "status": "VALID",
            "functions_count": len(functions),
            "classes_count": len(classes)
        }
    except SyntaxError as e:
        return {"status": "SYNTAX_ERROR", "msg": str(e)}
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

if __name__ == "__main__":
    res = inspect_file_ast(__file__)
    print(f"🔍 Inspección AST: Estado={res['status']} | Funciones={res.get('functions_count')} | Clases={res.get('classes_count')}")
