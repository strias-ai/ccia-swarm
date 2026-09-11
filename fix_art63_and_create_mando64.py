import os
import sys
import subprocess

print("=" * 80)
print("🛠️ 1. CORRIGIENDO DEUDA TÉCNICA (IMPORT SHUTIL) EN ARTEFACTO 63")
print("=" * 80)

art63_path = "/home/k1/ccia_workspace/modules/art_63.py"
with open(art63_path, "r", encoding="utf-8") as f:
    art63_code = f.read()

if "import shutil" not in art63_code:
    art63_code = "import shutil\n" + art63_code
    with open(art63_path, "w", encoding="utf-8") as f:
        f.write(art63_code)
    print("  ✅ 'import shutil' agregado con éxito al inicio de modules/art_63.py")

subprocess.run([sys.executable, "-m", "py_compile", art63_path], check=True)
print("  ✅ Módulo art_63.py recompilado sin errores.")

print("\n" + "=" * 80)
print("🛠️ 2. CREANDO CENTRO DE MANDO Y CONTROL DEL ARTEFACTO 64 (ccia_mando_64.py)")
print("=" * 80)

mando64_code = '''#!/usr/bin/env python3
import os
import sys
import sqlite3

_ws_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _ws_root not in sys.path:
    sys.path.insert(0, _ws_root)

from modules.art_64 import Artefact64EvolutionaryCompiler

def show_mando_64():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 80)
        print("🧬 CENTRO DE MANDO Y CONTROL: ARTEFACTO 64 (EVOLUTIONARY COMPILER & GENOME)")
        print("   Ruta DB Genoma: /home/k1/ccia_workspace/swarm_memory/genome_tree.db")
        print("=" * 80)
        print("  [1] 📜 Ver Historial Evolutivo y Diffs de un Script")
        print("  [2] 🧪 Testear Snippet de Código en Sandbox (Prueba AST + Fitness)")
        print("  [3] 🧬 Simular Mutación de Código (Parent vs Mutant Diff)")
        print("  [4] 📊 Ver Métricas Globales del Genoma en DB")
        print("  [5] 🧹 Mantenimiento de Memoria Genómica (Audit DB)")
        print("  [0] 🚪 Salir al Menú Principal")
        print("=" * 80)
        
        choice = input("CCiA-Mando-64> ").strip()
        
        if choice == "1":
            print("\\n📜 SCRIPTS EN REGISTRO GENÓMICO:")
            try:
                conn = sqlite3.connect(Artefact64EvolutionaryCompiler.DB_GENOME)
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT script_name FROM script_lineage")
                scripts = [r[0] for r in cur.fetchall()]
                conn.close()
                if scripts:
                    for idx, s in enumerate(scripts, 1):
                        print(f"  [{idx}] {s}")
                    s_name = input("\\nEscribe el nombre del script a inspeccionar (o ENTER para cancelar): ").strip()
                    if s_name:
                        history = Artefact64EvolutionaryCompiler.get_lineage_history(s_name)
                        print("\\n--- LINAJE RECUPERADO ---")
                        print(history)
                else:
                    print("  ⚠️ No hay scripts registrados aún en genome_tree.db.")
            except Exception as e:
                print(f"  ❌ Error consultando DB: {e}")
            input("\\n[Presiona ENTER para continuar...]")

        elif choice == "2":
            print("\\n🧪 INGRESA CÓDIGO PYTHON PARA PROBAR EN SANDBOX:")
            print("(Escribe/Pega el código. Finaliza con una línea que diga 'END'):\\n")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            sample_code = "\\n".join(lines)
            if sample_code.strip():
                res = Artefact64EvolutionaryCompiler.compile_and_test("manual_test.py", sample_code)
                print("\\n--- RESULTADO DE EVALUACIÓN ---")
                print(f"• Versión Genética: {res['version']}")
                print(f"• Score de Fitness: {res['fitness']}")
                print(f"• Líneas (+{res['added']} / -{res['deleted']})")
                print(f"• Log: {res['log']}")
            else:
                print("  ⚠️ Código vacío.")
            input("\\n[Presiona ENTER para continuar...]")

        elif choice == "3":
            print("\\n🧬 SIMULACIÓN DE MUTACIÓN DE CÓDIGO")
            p_code = "def process(x):\\n    return x * 2\\n"
            m_code = "def process(x):\\n    if x is None:\\n        return 0\\n    return x * 2\\n"
            print("  • Código Padre (Parent v1):\\n", p_code)
            print("  • Código Mutado (Mutant v2):\\n", m_code)
            
            res1 = Artefact64EvolutionaryCompiler.compile_and_test("demo_mutation.py", p_code)
            res2 = Artefact64EvolutionaryCompiler.compile_and_test("demo_mutation.py", m_code, parent_code=p_code)
            
            print("\\n--- RESULTADO MUTACIÓN V2 ---")
            print(f"• Fitness: {res2['fitness']} | Versión: {res2['version']}")
            print(f"• Diff:\\n{res2['diff']}")
            input("\\n[Presiona ENTER para continuar...]")

        elif choice == "4":
            print("\\n📊 MÉTRICAS GLOBALES DEL GENOMA:")
            try:
                conn = sqlite3.connect(Artefact64EvolutionaryCompiler.DB_GENOME)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*), AVG(fitness_score), SUM(lines_added), SUM(lines_deleted) FROM script_lineage")
                row = cur.fetchone()
                print(f"  • Total de Mutaciones Registradas : {row[0]}")
                print(f"  • Fitness Promedio                : {row[1] if row[1] else 0.0:.2f}")
                print(f"  • Total Líneas Añadidas (+)       : {row[2] if row[2] else 0}")
                print(f"  • Total Líneas Borradas (-)       : {row[3] if row[3] else 0}")
                conn.close()
            except Exception as e:
                print(f"  ❌ Error consultando métricas: {e}")
            input("\\n[Presiona ENTER para continuar...]")

        elif choice == "5":
            print("\\n🧹 AUDITORÍA Y TABLA DE BASE DE DATOS GENÓMICA:")
            if os.path.exists(Artefact64EvolutionaryCompiler.DB_GENOME):
                size = os.path.getsize(Artefact64EvolutionaryCompiler.DB_GENOME)
                print(f"  ✅ Archivo genome_tree.db presente ({size} bytes).")
            else:
                print("  ❌ Archivo genome_tree.db no encontrado.")
            input("\\n[Presiona ENTER para continuar...]")

        elif choice == "0":
            break

if __name__ == "__main__":
    show_mando_64()
'''

mando64_path = "/home/k1/ccia_workspace/ccia_mando_64.py"
with open(mando64_path, "w", encoding="utf-8") as f:
    f.write(mando64_code)

os.chmod(mando64_path, 0o755)
print("  ✅ Archivo ccia_mando_64.py creado y configurado con permisos de ejecución.")

subprocess.run([sys.executable, "-m", "py_compile", mando64_path], check=True)
print("  ✅ Compilación de verificación exitosa.")
print("=" * 80)
