import py_compile

def inject_queen_methods(filepath):
    print(f"🛠️ Inyectando load_queen_brains y save_queen_brains en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    queen_code = '''
    def load_queen_brains(self):
        queen_file = getattr(self, "queen_file", "/home/k1/ccia_workspace/queen_brains_63.json")
        if os.path.exists(queen_file):
            try:
                with open(queen_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return getattr(self, "DEFAULT_QUEEN_BRAINS", [
            {"code": "Q1", "role": "Reina Gobernanza & Estrategia", "icon": "👑", "model": "qwen2.5:coder"},
            {"code": "Q2", "role": "Reina Calidad & Seguridad", "icon": "🛡️", "model": "qwen2.5:coder"},
            {"code": "Q3", "role": "Reina Finanzas & Bounties", "icon": "💎", "model": "qwen2.5:coder"}
        ])

    def save_queen_brains(self):
        queen_file = getattr(self, "queen_file", "/home/k1/ccia_workspace/queen_brains_63.json")
        try:
            with open(queen_file, "w", encoding="utf-8") as f:
                json.dump(getattr(self, "queen_brains", []), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error guardando queen brains: {e}")
'''

    if "def load_queen_brains" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + queen_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

inject_queen_methods("/home/k1/ccia_workspace/modules/art_63.py")
inject_queen_methods("/home/k1/ccia_workspace/ccia_mando_63.py")
