import py_compile

def inject_daemon_methods(filepath):
    print(f"🛠️ Inyectando métodos de control de daemon en {filepath}...")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    daemon_code = '''
    def get_art63_daemon_status(self):
        pid_file = getattr(self, "daemon_pid_file", "/tmp/art63_daemon.pid")
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                return True, pid
            except (ValueError, OSError):
                pass
        return False, None

    def toggle_art62_247(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT status FROM ccia_artifact_manifests WHERE artifact_id = '62';")
            row = cur.fetchone()
            current_status = row[0] if row else "DISABLED"
            new_status = "ENABLED" if current_status != "ENABLED" else "DISABLED"
            cur.execute("INSERT OR REPLACE INTO ccia_artifact_manifests (artifact_id, status) VALUES ('62', ?);", (new_status,))
            conn.commit()
            conn.close()
            print(f"⚡ Estado Artefacto 62 actualizado a: {new_status}")
        except Exception as e:
            print(f"⚠️ Error al cambiar estado Artefacto 62: {e}")

    def toggle_art63_daemon(self):
        daemon_running, pid = self.get_art63_daemon_status()
        pid_file = getattr(self, "daemon_pid_file", "/tmp/art63_daemon.pid")
        log_file = getattr(self, "daemon_log_file", "/tmp/art63_daemon.log")
        if daemon_running and pid:
            try:
                os.kill(pid, 15)
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                print(f"🛑 Daemon Artefacto 63 (PID {pid}) detenido.")
            except Exception as e:
                print(f"⚠️ Error deteniendo Daemon: {e}")
        else:
            try:
                cmd = [sys.executable, "/home/k1/ccia_workspace/ccia_mando_63.py", "--daemon"]
                with open(log_file, "a") as log:
                    proc = subprocess.Popen(cmd, stdout=log, stderr=log, preexec_fn=os.setpgrp)
                with open(pid_file, "w") as f:
                    f.write(str(proc.pid))
                print(f"🟢 Daemon Artefacto 63 iniciado con PID: {proc.pid}")
            except Exception as e:
                print(f"⚠️ Error iniciando Daemon: {e}")
'''

    if "def get_art63_daemon_status" not in content:
        class_pos = content.find("class TriSwarmOrchestrator")
        if class_pos != -1:
            init_pos = content.find("def __init__", class_pos)
            if init_pos != -1:
                content = content[:init_pos] + daemon_code + "\n    " + content[init_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} REPARADO Y COMPILADO CON ÉXITO.")
    except Exception as e:
        print(f"  ❌ Error compilando {filepath}: {e}")

inject_daemon_methods("/home/k1/ccia_workspace/modules/art_63.py")
inject_daemon_methods("/home/k1/ccia_workspace/ccia_mando_63.py")
