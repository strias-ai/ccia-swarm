# -*- coding: utf-8 -*-
"""
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"
BACKUP_DIR = "/home/k1/ccia_workspace/backups"

def run_db_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_path = os.path.join(BACKUP_DIR, f"university_backup_{timestamp}.db")
    
    src_conn = sqlite3.connect(DB_PATH)
    dst_conn = sqlite3.connect(dest_path)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    
    return {"status": "SUCCESS", "backup_file": dest_path, "timestamp": timestamp}

if __name__ == "__main__":
    res = run_db_backup()
    print("✅ Respaldo seguro de university.db completado:", res)
