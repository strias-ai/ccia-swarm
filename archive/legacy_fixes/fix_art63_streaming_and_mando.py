import re
import os

print("=" * 80)
print("🔧 APLICANDO CORRECCIÓN TÉCNICA - ARTEFACTO 63, STREAMING & CENTRO DE MANDO")
print("=" * 80)

# 1. Patch a modules/art_63.py: Alias de método y volcado inmediato a log
art_63_path = "/home/k1/ccia_workspace/modules/art_63.py"

with open(art_63_path, "r", encoding="utf-8") as f:
    code = f.read()

# Crear alias implícito
if "call_ollama_direct = call_ollama_stream" not in code:
    code += "\n\n# Alias de compatibilidad con Centro de Mando\nTriSwarmOrchestrator.call_ollama_direct = TriSwarmOrchestrator.call_ollama_stream\n"

# Inyectar volcado a log e inserción de flush en streaming
log_stream_code = """
        log_file_path = "/tmp/art63_reasoning.log"
        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response, open(log_file_path, "a", encoding="utf-8") as log_f:
                header = f"\\n\\n🧠 [{role_code} - {role_name}] Modelo: {target_model}\\n" + "─"*70 + "\\n"
                sys.stdout.write(header)
                sys.stdout.flush()
                log_f.write(header)
                log_f.flush()
                
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        text_part = chunk.get("response", "")
                        full_response += text_part
                        sys.stdout.write(text_part)
                        sys.stdout.flush()
                        log_f.write(text_part)
                        log_f.flush()
                sys.stdout.write("\\n" + "─"*70 + "\\n")
                sys.stdout.flush()
        except Exception as e:"""

old_try_match = re.search(r'try:\s*req = urllib\.request\.Request\(.*?except Exception as e:', code, re.DOTALL)
if old_try_match and "log_file_path" not in code:
    code = code.replace(old_try_match.group(0), log_stream_code)

with open(art_63_path, "w", encoding="utf-8") as f:
    f.write(code)

print("  ✅ modules/art_63.py: Alias 'call_ollama_direct' asignado y flushing a /tmp/art63_reasoning.log activado.")

# 2. Patch a ccia_mando_63.py: Corrección Opción 13 y Opción 8 (Tail Monitor)
mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        mando_code = f.read()

    # Reemplazar invocaciones antiguas
    mando_code = mando_code.replace("orch.call_ollama_direct(", "orch.call_ollama_stream(")

    # Modificar opción 8 para hacer tailing en tiempo real del archivo de streaming
    option8_fix = """    elif option == "8":
        print("\\n📡 MONITOR DE RAZONAMIENTO EN TIEMPO REAL (LIVE OLLAMA STREAM)")
        print("🟢 Transmitiendo eventos y trazas del Swarm desde /tmp/art63_reasoning.log...")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("  [ Presione CTRL+C para salir del monitor y volver al menú ]\\n")
        log_file = "/tmp/art63_reasoning.log"
        if not os.path.exists(log_file):
            open(log_file, "w").close()
        try:
            subprocess.run(["tail", "-n", "100", "-f", log_file])
        except KeyboardInterrupt:
            print("\\n\\n🛑 Monitor finalizado.")
"""
    pattern = r'(elif|if)\s+option\s*==\s*["\']8["\']\s*:.*?(?=(elif|if|\n\s*def|\n\s*show_mando|\Z))'
    mando_code = re.sub(pattern, option8_fix + "\n", mando_code, flags=re.DOTALL)

    with open(mando_path, "w", encoding="utf-8") as f:
        f.write(mando_code)

    print("  ✅ ccia_mando_63.py: Opción 13 corregida y Opción 8 configurada con `tail -f`.")

