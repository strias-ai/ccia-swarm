# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_vram_governor_patch(code: str) -> str:
    old_opt8 = """        elif opt == "8":
            models = engine.get_installed_models()
            console.print(f"\\n🔍 [bold]Modelos detectados en Ollama:[/bold] {len(models)}")
            engine._purge_vram("qwen2.5-coder:3b")
            console.print("🧹 [bold green]VRAM Purge completada exitosamente.[/bold green]")
            Prompt.ask("\\nPresione ENTER para continuar")"""

    new_opt8 = """        elif opt == "8":
            import psutil
            models = engine.get_installed_models()
            mem = psutil.virtual_memory()
            vram_free_gb = mem.available / (1024 ** 3)
            
            console.print(f"\\n🔍 [bold]Modelos detectados en Ollama:[/bold] {len(models)}")
            console.print(f"🧠 [bold cyan]Memoria Libre APU/RAM:[/bold cyan] {vram_free_gb:.2f} GB")
            
            if vram_free_gb < 2.5:
                console.print("⚠️ [bold yellow]Memoria bajo el umbral crítico (<2.5GB). Ejecutando purga dinámicamente...[/bold yellow]")
                engine._purge_vram("qwen2.5-coder:3b")
                console.print("🧹 [bold green]Purga completada. Recursos liberados para la APU Radeon 780M.[/bold green]")
            else:
                console.print("✅ [bold green]Memoria holgada. No se requiere purga forzada.[/bold green]")
            Prompt.ask("\\nPresione ENTER para continuar")"""

    if old_opt8 in code:
        code = code.replace(old_opt8, new_opt8)
    return code

if __name__ == "__main__":
    compiler = CCIACompiler()
    success = compiler.compile_patch(
        apply_vram_governor_patch,
        module_name="apu_vram_governor_opt8",
        description="Gobernador dinámico de memoria compartida APU para la Opción 8"
    )
    sys.exit(0 if success else 1)
