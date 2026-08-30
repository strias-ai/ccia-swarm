# -*- coding: utf-8 -*-
"""
CCIA GIT AUTO-CHECKPOINT v1.0
Genera micro-commits automáticos tras compilaciones de parches o snapshots.
"""
import os
import subprocess
import time

def create_git_checkpoint(module_name: str) -> bool:
    repo_dir = os.path.dirname(__file__)
    try:
        if not os.path.exists(os.path.join(repo_dir, ".git")):
            subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "CCIA-CTO"], cwd=repo_dir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "ccia@nucbox-k11.local"], cwd=repo_dir, capture_output=True)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"checkpoint(ccia): módulo [{module_name}] integrado - {timestamp}"
        
        subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, capture_output=True)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    ok = create_git_checkpoint("test_module")
    print(f"📦 Git Checkpoint Status: {'OK' if ok else 'Fallback'}")
