import re
import py_compile

MC_PATH = "/home/k1/ccia_mission_control.py"

with open(MC_PATH, "r") as f:
    code = f.read()

# Bloque limpio de la Opción 3 (utilizando raw string r''' para evitar saltos de línea no deseados en la sustitución)
clean_option_3 = r'''elif sub_choice == "3":
            tbl = art.get("db_table") or art.get("target_table") or art.get("table")
            if not tbl and art.get("manifest_json"):
                try:
                    m = json.loads(art["manifest_json"])
                    tbl = m.get("table") or m.get("db_table") or m.get("target_table")
                except Exception:
                    pass
            if not tbl:
                tbl = "ccia_artifact_manifests"

            try:
                cur.execute(f"SELECT * FROM {tbl} ORDER BY ROWID DESC LIMIT 5;")
                rows = cur.fetchall()
                print(f"\n📊 Registros Recientes en Tabla '{tbl}':")
                if not rows:
                    print("  (Sin registros en esta tabla aún)")
                for r in rows:
                    print(f"  • {r}")
            except Exception as e:
                print(f"\n⚠️ Error consultando '{tbl}': {e}")
                cur.execute("SELECT * FROM ccia_artifact_manifests ORDER BY ROWID DESC LIMIT 5;")
                rows = cur.fetchall()
                print(f"\n📊 Registros Recientes en Tabla 'ccia_artifact_manifests' (Fallback):")
                for r in rows:
                    print(f"  • {r}")'''

pattern = r'elif sub_choice == ["\']3["\']:[\s\S]*?(?=elif sub_choice == ["\']4["\'])'

if re.search(pattern, code):
    code = re.sub(pattern, clean_option_3 + "\n        ", code)
    with open(MC_PATH, "w") as f:
        f.write(code)
    py_compile.compile(MC_PATH, doraise=True)
    print("🟢 Misión Control corregido y validado mediante py_compile.")
else:
    print("⚠️ No se encontró la estructura de sub_choice '3'.")
