import py_compile

def inject_brains_methods(filepath):
    print(f"🛠️ Verificando e inyectando load_brains/save_brains en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    load_brains_code = '''
    def load_brains(self):
        brains_file = getattr(self, "brains_file", "/home/k1/ccia_workspace/swarm_brains_63.json")
        if os.path.exists(brains_file):
            try:
                with open(brains_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return getattr(self, "DEFAULT_BRAINS", [
            {"code": "1.1", "role": "Archi-Investigador", "icon": "🔍", "model": "qwen2.5:coder"},
            {"code": "1.2", "role": "Archi-Diseñador", "icon": "📐", "model": "qwen2.5:coder"},
            {"code": "1.3", "role": "Especialista Backend", "icon": "⚙️", "model": "qwen2.5:coder"},
            {"code": "1.4", "role": "Especialista Frontend", "icon": "🎨", "model": "qwen2.5:coder"},
            {"code": "1.5", "role": "Auditor Seguridad", "icon": "🛡️", "model": "qwen2.5:coder"},
            {"code": "2.1", "role": "Critico Código", "icon": "🧪", "model": "qwen2.5:coder"},
            {"code": "2.2", "role": "Optimizador Rendimiento", "icon": "⚡", "model": "qwen2.5:coder"},
            {"code": "2.3", "role": "Ingeniero Pruebas", "icon": "🎯", "model": "qwen2.5:coder"},
            {"code": "2.4", "role": "Redactor Docs", "icon": "📝", "model": "qwen2.5:coder"},
            {"code": "2.5", "role": "Integrador API", "icon": "🔌", "model": "qwen2.5:coder"},
            {"code": "3.1", "role": "Arbitro Calidad", "icon": "⚖️", "model": "qwen2.5:coder"},
            {"code": "3.2", "role": "Estratega Bounties", "icon": "💰", "model": "qwen2.5:coder"},
            {"code": "3.3", "role": "Especialista DB", "icon": "🗄️", "model": "qwen2.5:coder"},
            {"code": "3.4", "role": "Gestor Despliegue", "icon": "🚀", "model": "qwen2.5:coder"},
            {"code": "3.5", "role": "Reina Mando", "icon": "👑", "model": "qwen2.5:coder"}
        ])

    def save_brains(self):
        brains_file = getattr(self, "brains_file", "/home/k1/ccia_workspace/swarm_brains_63.json")
        try:
            with open(brains_file, "w", encoding="utf-8") as f:
                json.dump(self.brains, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error guardando brains: {e}")
'''

    if "def load_brains" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + load_brains_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} ACTUALIZADO Y VALIDADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

inject_brains_methods("/home/k1/ccia_workspace/modules/art_63.py")
inject_brains_methods("/home/k1/ccia_workspace/ccia_mando_63.py")
