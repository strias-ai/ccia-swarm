import re

path = "/home/k1/ccia_workspace/modules/stripe_live_sync.py"
with open(path, "r") as f:
    code = f.read()

# Evitar reinsertar eventos ya procesados en revenue_settlements
if "WHERE source_event = " not in code:
    code = code.replace(
        "INSERT INTO revenue_settlements",
        "INSERT OR IGNORE INTO revenue_settlements"
    )
    with open(path, "w") as f:
        f.write(code)
    print("✅ Guardado parche de idempotencia estricta en stripe_live_sync.py")
else:
    print("ℹ️ El script ya cuenta con control de idempotencia.")
