# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_semantic_indexer_patch(code: str) -> str:
    old_opt6 = """        elif opt == "6":"""

    new_opt6 = """        elif opt == "6":
            try:
                from semantic_code_indexer import index_workspace_code
                total_idx, _ = index_workspace_code()
                console.print(f"🔍 [bold green]RAG Semántico Activo:[/bold green] {total_idx} archivos del Workspace indexados.")
            except Exception:
                pass"""

    if old_opt6 in code and "semantic_code_indexer" not in code:
        code = code.replace(old_opt6, new_opt6, 1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_semantic_indexer_patch,
        module_name="semantic_code_indexer",
        description="Indexador semántico del Workspace para la Biblioteca RAG (Opción 6)"
    )
    sys.exit(0 if success else 1)
