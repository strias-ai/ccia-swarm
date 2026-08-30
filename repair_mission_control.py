import os
import sys
import re
import py_compile

MC_PATH = "/home/k1/ccia_mission_control.py"

if not os.path.exists(MC_PATH):
    print(f"🔴 No se encontró {MC_PATH}")
    sys.exit(1)

with open(MC_PATH, "r") as f:
    code = f.read()

# Sustitución limpia de la función artifact_submenu
new_function = '''def artifact_submenu(art_key, art):
    while True:
        print("\\n" + "─"*78)
        print(f"  PROYECTO/ARTEFACTO: {art.get('name', 'Sin nombre')} ({art.get('version', 'v1.0')})")
        print(f"  Categoría: {art.get('category', 'General')}")
        print(f"  Script Target: {art.get('main_script', 'N/A')}")
        print("─"*78)
        print("  1. 🚀 Ejecutar Artefacto / Módulo")
        print("  2. 📜 Ver Manifiesto Fundacional (JSON Cascada en Terminal)")
        print("  3. 📊 Consultar Registros DB Relacionados")
        print("  4. 📜 Ver Archivo de Logs en Tiempo Real")
        print("  5. 🧪 Verificar Certificación AST (py_compile)")
        print("  6. ⬅️  Volver al Menú Principal")
        
        sub_choice = input("\\nCCIA-Submenu> ").strip()
        
        if sub_choice == "1":
            script = art.get("main_script")
            if script and os.path.exists(script):
                print(f"\\n🚀 Ejecutando {script}...")
                os.system(f"python3 {script}")
            else:
                print(f"\\n❌ Error: Script target no existe o no configurado ({script}).")
            input("\\nPresione ENTER para continuar...")
        elif sub_choice == "2":
            print("\\n📜 Manifiesto JSON:")
            import json
            print(json.dumps(art, indent=2, ensure_ascii=False))
            input("\\nPresione ENTER para continuar...")
        elif sub_choice == "3":
            tbl = art.get("table") or "ccia_artifact_manifests"
            print(f"\\n📊 Registros Recientes en Tabla '{tbl}':")
            try:
                import sqlite3
                conn = sqlite3.connect("/home/k1/ccia_workspace/university.db")
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {tbl} LIMIT 5")
                rows = cur.fetchall()
                for r in rows:
                    print(f"  • {r}")
                conn.close()
            except Exception as e:
                print(f"❌ Error DB: {e}")
            input("\\nPresione ENTER para continuar...")
        elif sub_choice == "4":
            log_file = art.get("log") or "/home/k1/ccia_workspace/cron_repos.log"
            if log_file and os.path.exists(str(log_file)):
                print(f"\\n📜 Mostrando últimas 20 líneas de {log_file}:\\n")
                os.system(f"tail -n 20 {log_file}")
            else:
                print(f"\\n⚠️ Archivo de log no encontrado o no configurado ({log_file}).")
            input("\\nPresione ENTER para continuar...")
        elif sub_choice == "5":
            script = art.get("main_script")
            if script and os.path.exists(script):
                try:
                    py_compile.compile(script, doraise=True)
                    print(f"\\n✅ Certificación AST Vigente: {script} sin errores de sintaxis.")
                except Exception as e:
                    print(f"\\n🔴 Error de Certificación AST: {e}")
            else:
                print(f"\\n❌ Script target no válido para AST ({script}).")
            input("\\nPresione ENTER para continuar...")
        elif sub_choice == "6":
            break
'''

# Reemplazar bloque desalineado de la función
parts = code.split("def artifact_submenu")
head = parts[0]
tail_match = re.search(r"\n(def [a-zA-Z0-9_]+\(|if __name__)", parts[1])

if tail_match:
    tail = parts[1][tail_match.start():]
    fixed_code = head + new_function + "\n" + tail
else:
    fixed_code = head + new_function

with open(MC_PATH, "w") as f:
    f.write(fixed_code)

# Certificación de compilación AST
try:
    py_compile.compile(MC_PATH, doraise=True)
    print("🟢 AST Certification OK: /home/k1/ccia_mission_control.py restaurado sin errores de sintaxis.")
except py_compile.PyCompileError as e:
    print(f"🔴 Error AST: {e}")
