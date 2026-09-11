import re
import py_compile

def fix_file(path):
    print("Reparando:", path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Reemplazar 'continue' huérfanos por 'pass'
    lines = content.splitlines(True)
    new_lines = []
    for line in lines:
        if line.strip() == "continue":
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + "pass\n")
        else:
            new_lines.append(line)
    content = "".join(new_lines)

    # 2. Inyectar método toggle_art62_247 con sangría limpia y 'icon' definido
    m_code = (
        "    def toggle_art62_247(self):\n"
        "        try:\n"
        "            conn = sqlite3.connect(self.db_path)\n"
        "            cur = conn.cursor()\n"
        "            cur.execute(\n"
        "                \"SELECT status FROM ccia_artifact_manifests \"\n"
        "                \"WHERE artifact_id = '62';\"\n"
        "            )\n"
        "            row = cur.fetchone()\n"
        "            current_status = row[0] if row else \"DISABLED\"\n"
        "            st_u = str(current_status).upper()\n"
        "            is_act = \"ENABLE\" in st_u or \"ACT\" in st_u\n"
        "            new_status = \"DISABLED\" if is_act else \"ENABLED\"\n"
        "            cur.execute(\n"
        "                \"UPDATE ccia_artifact_manifests SET status = ? \"\n"
        "                \"WHERE artifact_id = '62';\",\n"
        "                (new_status,)\n"
        "            )\n"
        "            conn.commit()\n"
        "            conn.close()\n"
        "            new_u = str(new_status).upper()\n"
        "            i_act = \"ENABLE\" in new_u or \"ACT\" in new_u\n"
        "            icon = \"🟢\" if i_act else \"🔴\"\n"
        "            msg = f\"\\n{icon} BUCLE 24/7 ARTEFACTO 62 CAMBIADO A: [{new_status}]\"\n"
        "            print(msg)\n"
        "        except Exception as e:\n"
        "            print(f\"\\n⚠️ Error cambiando estado de Artefacto 62: {e}\")"
    )

    pat = r"\n\s*def toggle_art62_247\(self\):.*?(?=\n\s*def |\n\s*if __name__|\Z)"
    if re.search(pat, content, flags=re.DOTALL):
        content = re.sub(pat, "\n\n" + m_code, content, count=1, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(path, doraise=True)
        print("  -> COMPILADO CON ÉXITO")
    except Exception as e:
        print("  -> ERROR:", e)

fix_file("/home/k1/ccia_workspace/modules/art_63.py")
fix_file("/home/k1/ccia_workspace/ccia_mando_63.py")
