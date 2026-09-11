import py_compile

mc_path = "/home/k1/ccia_mission_control.py"

with open(mc_path, "r") as f:
    code = f.read()

# Asegurar import de py_compile al inicio del archivo
if "import py_compile" not in code:
    code = "import py_compile\n" + code

with open(mc_path, "w") as f:
    f.write(code)

py_compile.compile(mc_path, doraise=True)
print("🟢 ccia_mission_control.py parcheado con py_compile y verificado con AST.")
