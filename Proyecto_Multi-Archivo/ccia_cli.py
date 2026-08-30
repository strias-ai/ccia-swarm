# -*- coding: utf-8 -*-
import sqlite3
import sys

DB_PATH = "/home/k1/ccia_workspace/university.db"

def show_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n==========================================")
    print("      PANEL DE MANDO Y CONTROL CCIA      ")
    print("==========================================")
    
    cursor.execute("SELECT api_key, client_name, credits, total_requests FROM api_clients")
    clients = cursor.fetchall()
    print("\n--- CLIENTES Y CRÉDITOS ---")
    for c in clients:
        print(f"Key: {c[0]} | Cliente: {c[1]} | Créditos: {c[2]} | Peticiones: {c[3]}")
        
    cursor.execute("SELECT service, status FROM system_credentials")
    creds = cursor.fetchall()
    print("\n--- VAULT DE CREDENCIALES ---")
    for cr in creds:
        print(f"Servicio: {cr[0]} | Estado: {cr[1]}")
    conn.close()

if __name__ == "__main__":
    show_status()
