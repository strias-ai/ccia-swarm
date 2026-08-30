import re

mc_path = "/home/k1/ccia_mission_control.py"

with open(mc_path, "r") as f:
    code = f.read()

# Parche para la comprobación de logs (evita el TypeError de NoneType)
code = re.sub(
    r'if os\.path\.exists\(art\["log"\]\):',
    'log_path = art.get("log");\n    if log_path and os.path.exists(str(log_path)):',
    code
)

# Parche para la consulta de tabla (evita el Error DB: no such table: None)
code = re.sub(
    r'tbl = art\["table"\]',
    'tbl = art.get("table") or "ccia_artifact_manifests"',
    code
)

with open(mc_path, "w") as f:
    f.write(code)

print("🟢 ccia_mission_control.py parcheado correctamente.")
