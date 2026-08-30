# -*- coding: utf-8 -*-
"""
CCIA LOG ROTATION JANITOR v1.0
Rota y purga archivos .log pesados en el Workspace para mantener el espacio optimizado.
"""
import os
import glob

MAX_LOG_SIZE_MB = 10.0

def cleanup_old_logs(workspace_path: str = "/home/k1/ccia_workspace") -> dict:
    log_files = glob.glob(f"{workspace_path}/**/*.log", recursive=True)
    purged = 0
    reclaimed_bytes = 0

    for log_f in log_files:
        try:
            size_bytes = os.path.getsize(log_f)
            size_mb = size_bytes / (1024 * 1024)
            if size_mb > MAX_LOG_SIZE_MB:
                reclaimed_bytes += size_bytes
                with open(log_f, "w", encoding="utf-8") as f:
                    f.write("--- Log rotado automáticamente por CCIA Janitor ---\n")
                purged += 1
        except Exception:
            pass

    return {
        "logs_rotated": purged,
        "space_saved_mb": round(reclaimed_bytes / (1024 * 1024), 2)
    }

if __name__ == "__main__":
    res = cleanup_old_logs()
    print(f"🧹 Janitor de Logs: {res['logs_rotated']} rotados | {res['space_saved_mb']} MB liberados")
