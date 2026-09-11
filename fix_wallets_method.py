import py_compile

def inject_wallets_methods(filepath):
    print(f"🛠️ Inyectando load_wallets y save_wallets en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    wallets_code = '''
    def load_wallets(self):
        wallets_file = getattr(self, "wallets_file", "/home/k1/ccia_workspace/wallets_63.json")
        if os.path.exists(wallets_file):
            try:
                with open(wallets_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return getattr(self, "DEFAULT_WALLETS", {
            "lightning": "vellichorlate475846@getalby.com",
            "evm": "0x6040f4D8BA36214222d34E176634670407a9bC56",
            "btc": "bc1q6x7ejwx23ucr2wjk5cewxg4d3tsdzxfjvt3t59",
            "solana": "",
            "ton": "",
            "sui": "",
            "near": ""
        })

    def save_wallets(self):
        wallets_file = getattr(self, "wallets_file", "/home/k1/ccia_workspace/wallets_63.json")
        try:
            with open(wallets_file, "w", encoding="utf-8") as f:
                json.dump(getattr(self, "wallets", {}), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error guardando carteras: {e}")
'''

    if "def load_wallets" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + wallets_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

inject_wallets_methods("/home/k1/ccia_workspace/modules/art_63.py")
inject_wallets_methods("/home/k1/ccia_workspace/ccia_mando_63.py")
