# -*- coding: utf-8 -*-
"""
CCIA GIT AUTO SNAPSHOT VAULT v1.0
Gestiona checkpoints automáticos y puntos de restauración Git en Opción 8.
"""
import subprocess
import time

def create_git_snapshot(reason: str = "auto_checkpoint") -> dict:
    try:
        timestamp = int(time.time())
        commit_msg = f"CCIA Vault Snapshot [{timestamp}]: {reason}"
        subprocess.run(["git", "add", "-A"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
        
        if res.returncode == 0:
            return {"status": "CREATED", "msg": commit_msg}
        elif "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
            return {"status": "CLEAN", "msg": "Workspace sin cambios pendientes"}
        return {"status": "ERROR", "msg": res.stderr.strip()}
    except Exception as e:
        return {"status": "EXCEPT", "msg": str(e)}

if __name__ == "__main__":
    print(create_git_snapshot("test_execution"))
