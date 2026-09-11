import os
import sqlite3
import re
import py_compile

WORKSPACE = "/home/k1/ccia_workspace"
ART63_PATH = os.path.join(WORKSPACE, "modules", "art_63.py")
MANDO_PATH = os.path.join(WORKSPACE, "ccia_mando_63.py")
DB_PATH = os.path.join(WORKSPACE, "ccia_bounties.db")

print("=" * 80)
print("🛠️ ACTIVACIÓN REAL DE DAEMON [12] Y NAVEGACIÓN DINÁMICA DB PARA [3]")
print("=" * 80)

# 1. PURGA COMPLETA Y CAMBIO DE ESTADO EN SQLITE
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE bounty_opportunities SET status='SKIPPED' WHERE repo LIKE '%comment-auto-bot%' OR issue_url LIKE '%comment-auto-bot%'")
    cursor.execute("DELETE FROM bounty_opportunities WHERE repo LIKE '%comment-auto-bot%' OR issue_url LIKE '%comment-auto-bot%'")
    conn.commit()
    
    cursor.execute("SELECT id, repo, title, issue_url FROM bounty_opportunities WHERE status='PENDING' ORDER BY id ASC LIMIT 1")
    next_item = cursor.fetchone()
    conn.close()
    
    if next_item:
        print(f"  ✅ Siguiente tarea real en cola: [{next_item[0]}] {next_item[1]} -> {next_item[2]}")
    else:
        print("  ⚠️ No se encontraron elementos PENDING.")

# 2. PARCHEAR art_63.py PARA EXTRAER DINÁMICAMENTE DE LA BASE DE DATOS
with open(ART63_PATH, "r", encoding="utf-8") as f:
    art_code = f.read()

# Reemplazar la asignación fija de comment-auto-bot por consulta dinámica SQL
old_fallback = 'issue_url = issue_url or "https://github.com/karthikabinav/comment-auto-bot/issues/2351"'
new_dynamic = '''
        if not issue_url or "comment-auto-bot" in issue_url:
            try:
                conn = sqlite3.connect("/home/k1/ccia_workspace/ccia_bounties.db")
                c = conn.cursor()
                c.execute("SELECT issue_url, repo, title FROM bounty_opportunities WHERE status='PENDING' AND repo NOT LIKE '%comment-auto-bot%' ORDER BY id ASC LIMIT 1")
                row = c.fetchone()
                if row:
                    issue_url, repo, title = row[0], row[1], row[2]
                    c.execute("UPDATE bounty_opportunities SET status='PROCESSING' WHERE issue_url=?", (issue_url,))
                    conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error extrayendo de DB: {e}")
'''

if "comment-auto-bot" in art_code:
    art_code = re.sub(r'.*comment-auto-bot.*', new_dynamic, art_code)

with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(art_code)

print("  ✅ Módulo art_63.py actualizado para consumo dinámico de cola.")

# 3. VINCULAR LA OPCIÓN [12] A UN PROCESO EN SEGUNDO PLANO
with open(MANDO_PATH, "r", encoding="utf-8") as f:
    mando_code = f.read()

daemon_launch_code = '''
def toggle_daemon():
    pid_file = "/tmp/art63_daemon.pid"
    log_file = "/tmp/art63_reasoning.log"
    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 9)
        except Exception:
            pass
        os.remove(pid_file)
        print("🔴 Daemon Artefacto 63 DETENIDO.")
    else:
        with open(log_file, "a") as f_out:
            p = subprocess.Popen(["python3", "/home/k1/ccia_workspace/modules/art_63.py"], stdout=f_out, stderr=f_out)
            with open(pid_file, "w") as f_pid:
                f_pid.write(str(p.pid))
        print(f"🟢 Daemon Artefacto 63 ARRANCADO en segundo plano (PID: {p.pid}).")
'''

if "def toggle_daemon" not in mando_code:
    mando_code += "\n" + daemon_launch_code

with open(MANDO_PATH, "w", encoding="utf-8") as f:
    f.write(mando_code)

print("  ✅ Opción [12] vinculada al proceso demonio en segundo plano.")

# 4. COMPILACIÓN Y VERIFICACIÓN
try:
    py_compile.compile(ART63_PATH, doraise=True)
    py_compile.compile(MANDO_PATH, doraise=True)
    print("  ✅ Compilación finalizada sin errores.")
except py_compile.PyCompileError as e:
    print(f"  ❌ Error de compilación:\n{e}")

print("=" * 80)
