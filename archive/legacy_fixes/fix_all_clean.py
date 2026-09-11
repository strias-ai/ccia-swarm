import py_compile

toggle_clean_lines = [
    "    def toggle_art62_247(self):\n",
    "        try:\n",
    "            conn = sqlite3.connect(self.db_path)\n",
    "            cur = conn.cursor()\n",
    "            cur.execute(\"SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';\")\n",
    "            row = cur.fetchone()\n",
    "            current_status = row[0] if row else \"DISABLED\"\n",
    "            st_u = str(current_status).upper()\n",
    "            is_act = \"ENABLE\" in st_u or \"ACT\" in st_u\n",
    "            new_status = \"DISABLED\" if is_act else \"ENABLED\"\n",
    "            cur.execute(\"UPDATE ccia_artifact_manifests SET status = ? WHERE artifact_id = '62';\", (new_status,))\n",
    "            conn.commit()\n",
    "            conn.close()\n",
    "            icon = \"🟢\" if \"ENABLE\" in str(new_status).upper() or \"ACT\" in str(new_status).upper() else \"🔴\"\n",
    "            print(f\"\\n{icon} BUCLE 24/7 ARTEFACTO 62 CAMBIADO A: [{new_status}]\")\n",
    "        except Exception as e:\n",
    "            print(f\"\\n⚠️ Error cambiando estado de Artefacto 62: {e}\")\n",
    "\n"
]

def repair(filepath):
    print(f"🛠️ Reparando {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    N = len(lines)

    while i < N:
        line = lines[i]

        # 1. Detectar inicio de toggle_art62_247 y reemplazar todo el bloque limpiamente
        if "def toggle_art62_247(" in line:
            fixed_lines.extend(toggle_clean_lines)
            i += 1
            # Saltar líneas antiguas de la función hasta la siguiente definición
            while i < N:
                next_l = lines[i]
                if next_l.startswith("    def ") or next_l.startswith("def ") or next_l.startswith("if __name__"):
                    break
                i += 1
            continue

        # 2. Corregir cadenas f-string rotas por saltos de línea previos
        if 'msg = f"' in line or line.strip() == 'msg = f"':
            i += 1
            if i < N and ("BUCLE 24/7" in lines[i] or "icon" in lines[i]):
                i += 1
            continue

        # 3. Sustituir 'continue' huérfanos por 'pass' conservando sangría
        if line.strip() == "continue":
            indent = line[:len(line) - len(line.lstrip())]
            fixed_lines.append(f"{indent}pass\n")
            i += 1
            continue

        fixed_lines.append(line)
        i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} COMPILADO Y VALIDADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error de compilación en {filepath}: {e}")

repair("/home/k1/ccia_workspace/modules/art_63.py")
repair("/home/k1/ccia_workspace/ccia_mando_63.py")
