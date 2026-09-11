import py_compile
import subprocess

CASCADE_PATH = "/home/k1/ccia_workspace/cascade_auditor.py"

with open(CASCADE_PATH, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("if art_id == 24:", "if int(art_id) == 24:")

with open(CASCADE_PATH, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(CASCADE_PATH, doraise=True)

print("⚡ Auditor en cascada ajustado. Ejecutando reporte final...\n")
subprocess.run(["python3", CASCADE_PATH])
