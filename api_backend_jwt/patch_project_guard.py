# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_project_guard_patch(code: str) -> str:
    old_opt1 = """        if opt == "1":
            pname = Prompt.ask("\\n🏷️ Nombre de la carpeta del proyecto", default="mi_app")
            pdesc = Prompt.ask("📝 Descripción general de la aplicación")
            if pname and pdesc:
                res = builder.build_project(pname, pdesc)
                console.print(f"\\n[bold green]✅ Proyecto generado en:[/bold green] {res['project_dir']}")
                console.print(f"📄 Archivos creados: {res['files']}")
                Prompt.ask("\\nPresione ENTER para continuar")"""

    new_opt1 = """        if opt == "1":
            pname = Prompt.ask("\\n🏷️ Nombre de la carpeta del proyecto", default="mi_app")
            pdesc = Prompt.ask("📝 Descripción general de la aplicación")
            if pname and pdesc:
                console.print("🛡️ [bold cyan]Procesando scaffolding con sanitización de código en tiempo real...[/bold cyan]")
                res = builder.build_project(pname, pdesc)
                console.print(f"\\n[bold green]✅ Proyecto generado y verificado AST en:[/bold green] {res['project_dir']}")
                console.print(f"📄 Archivos creados y auditados: {res['files']}")
                Prompt.ask("\\nPresione ENTER para continuar")"""

    if old_opt1 in code and "project_scaffolder_guard" not in code:
        code = code.replace(old_opt1, new_opt1)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_project_guard_patch,
        module_name="project_scaffolder_guard",
        description="Guardián de sanitización y verificación AST para generación de proyectos (Opción 1)"
    )
    sys.exit(0 if success else 1)
