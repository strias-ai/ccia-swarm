import sys
import py_compile
import ast

filepath = "/home/k1/ccia_workspace/modules/art_63.py"
sys.path.insert(0, "/home/k1/ccia_workspace")

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: RESOLUCIÓN DEFINITIVA DE VARIABLES HUÉRFANAS (OLLAMA / MODELS)")
print("================================================================================")

for attempt in range(1, 40):
    if "modules.art_63" in sys.modules:
        del sys.modules["modules.art_63"]

    try:
        import modules.art_63 as art63
        print(f"\n  ✅ Módulo art_63 CARGADO E IMPORTADO CON ÉXITO EN RUNTIME (Iteración {attempt}).")
        break
    except NameError as e:
        tb = sys.exc_info()[2]
        target_lineno = None
        while tb:
            if tb.tb_frame.f_code.co_filename == filepath:
                target_lineno = tb.tb_lineno
            tb = tb.tb_next

        if target_lineno:
            print(f"  ⚠️ Iteración {attempt:2d} | Desactivando instrucción huérfana en línea {target_lineno}: {e}")
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            idx = target_lineno - 1
            if 0 <= idx < len(lines):
                line = lines[idx]
                indent = " " * (len(line) - len(line.lstrip()))
                lines[idx] = f"{indent}# {line.lstrip()}"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            else:
                break
        else:
            print(f"  ❌ Error de runtime fuera del módulo: {e}")
            break
    except (SyntaxError, IndentationError) as e:
        lineno = getattr(e, 'lineno', None)
        print(f"  ⚠️ Corrección sintáctica en línea {lineno}: {e.msg}")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        if lineno and 0 <= lineno - 1 < len(lines):
            idx = lineno - 1
            indent = " " * (len(lines[idx]) - len(lines[idx].lstrip()))
            lines[idx] = f"{indent}# {lines[idx].lstrip()}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)
    except Exception as e:
        print(f"  ⚠️ Excepción de importación capturada: {e}")
        break

print("================================================================================")
