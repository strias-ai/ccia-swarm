# -*- coding: utf-8 -*-
"""
CCIA AST DEPENDENCY GRAPH BUILDER v1.0
Analiza relaciones de importación entre archivos Python del Workspace (Opción 6).
"""
import ast
import glob
import os

def build_dependency_graph(workspace_path: str = "/home/k1/ccia_workspace") -> dict:
    graph = {}
    py_files = glob.glob(f"{workspace_path}/**/*.py", recursive=True)

    for file_path in py_files:
        mod_name = os.path.basename(file_path).replace(".py", "")
        imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass

        graph[mod_name] = sorted(list(set(imports)))

    return {
        "total_modules": len(graph),
        "graph": graph
    }

if __name__ == "__main__":
    res = build_dependency_graph()
    print(f"🕸️ Grafo de Dependencias: {res['total_modules']} módulos mapeados")
