import os
import ast

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"

if not os.path.exists(art63_path):
    print(f"❌ No se encontró el archivo {art63_path}")
else:
    with open(art63_path, "r", encoding="utf-8") as f:
        source = f.read()

    print("=" * 80)
    print("🔍 AUDITORÍA DE ESTRUCTURA: modules/art_63.py")
    print("=" * 80)

    try:
        tree = ast.parse(source)
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        print(f"• Clases detectadas: {classes}")
        print(f"• Funciones/Métodos detectados ({len(functions)}): {functions[:15]}...")
        
        # Verificar presencia de variables/métodos clave de la deuda técnica
        print("\nVerificación de Puntos Críticos:")
        print(f"  - Contexto de Git/Issue (body): {'`body`' in source or 'issue_body' in source}")
        print(f"  - Manejo de Fallback/Timeout: {'timeout' in source}")
        print(f"  - Filtro de Streaming (<think>): {'<think>' in source}")
        print(f"  - Token GitHub (GITHUB_TOKEN): {'GITHUB_TOKEN' in source or 'GH_PAT' in source}")

    except Exception as e:
        print(f"⚠️ Error parsing AST: {e}")

print("=" * 80)
