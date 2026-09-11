import re
import py_compile

MC_PATH = "/home/k1/ccia_mission_control.py"

with open(MC_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'elif sub_choice == "3":' in line or "elif sub_choice == '3':" in line:
        start_idx = i
    elif start_idx is not None and ('elif sub_choice == "4":' in line or "elif sub_choice == '4':" in line):
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    new_block = [
        '        elif sub_choice == "3":\n',
        '            tbl = art.get("db_table") or art.get("target_table") or art.get("table")\n',
        '            if not tbl and art.get("manifest_json"):\n',
        '                try:\n',
        '                    m = json.loads(art["manifest_json"])\n',
        '                    tbl = m.get("table") or m.get("db_table") or m.get("target_table")\n',
        '                except Exception:\n',
        '                    pass\n',
        '            if not tbl or tbl == "None":\n',
        '                art_id = str(art.get("artifact_id") or art.get("id") or "")\n',
        '                art_name = str(art.get("name") or "")\n',
        '                if "25" in art_id or "hapax" in art_name.lower():\n',
        '                    tbl = "vant_agent_telemetry"\n',
        '                elif "26" in art_id or "anhydro" in art_name.lower():\n',
        '                    tbl = "anhydro_vault"\n',
        '                elif "27" in art_id or "28" in art_id or "health" in art_name.lower() or "chronos" in art_name.lower():\n',
        '                    tbl = "system_health_logs"\n',
        '                else:\n',
        '                    tbl = "ccia_artifact_manifests"\n',
        '\n',
        '            try:\n',
        '                conn_3 = sqlite3.connect("/home/k1/ccia_workspace/university.db")\n',
        '                cur_3 = conn_3.cursor()\n',
        '                cur_3.execute(f"SELECT * FROM {tbl} ORDER BY ROWID DESC LIMIT 5;")\n',
        '                rows = cur_3.fetchall()\n',
        '                print(f"\\n📊 Registros Recientes en Tabla \'{tbl}\':")\n',
        '                if not rows:\n',
        '                    print("  (Sin registros en esta tabla aún)")\n',
        '                for r in rows:\n',
        '                    print(f"  • {r}")\n',
        '                conn_3.close()\n',
        '            except Exception as e:\n',
        '                print(f"\\n⚠️ Error consultando \'{tbl}\': {e}")\n',
        '                try:\n',
        '                    conn_fb = sqlite3.connect("/home/k1/ccia_workspace/university.db")\n',
        '                    cur_fb = conn_fb.cursor()\n',
        '                    cur_fb.execute("SELECT * FROM ccia_artifact_manifests ORDER BY ROWID DESC LIMIT 5;")\n',
        '                    rows = cur_fb.fetchall()\n',
        '                    print("\\n📊 Registros Recientes en Tabla \'ccia_artifact_manifests\' (Fallback):")\n',
        '                    for r in rows:\n',
        '                        print(f"  • {r}")\n',
        '                    conn_fb.close()\n',
        '                except Exception as e2:\n',
        '                    print(f"  Error fallback: {e2}")\n'
    ]
    
    lines[start_idx:end_idx] = new_block
    
    with open(MC_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    py_compile.compile(MC_PATH, doraise=True)
    print("🟢 Conexión a base de datos aislada e inmunizada en Misión Control para la opción [3].")
else:
    print(f"⚠️ No se localizó la sección a reemplazar (start_idx={start_idx}, end_idx={end_idx}).")
