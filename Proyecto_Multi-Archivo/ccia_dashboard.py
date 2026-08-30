# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import sqlite3
import time
import re

DB_PATH = "/home/k1/ccia_workspace/university.db"
PROJ_DIR = "/home/k1/ccia_workspace/Proyecto_Multi-Archivo"

def get_db():
    return sqlite3.connect(DB_PATH)

def show_status():
    conn = get_db()
    cursor = conn.cursor()
    print("\n" + "="*50)
    print("       PANEL DE MANDO Y CONTROL CCIA v2.0       ")
    print("="*50)
    
    # 1. Estado de Créditos y Clientes
    cursor.execute("SELECT client_name, credits, total_requests FROM api_clients")
    clients = cursor.fetchall()
    print("\n--- 💳 CLIENTES & CRÉDITOS ---")
    for c in clients:
        print(f"  • {c[0]}: {c[1]} créditos restantes ({c[2]} peticiones)")
        
    # 2. Última URL Pública del Túnel
    cursor.execute("SELECT url, created_at FROM public_tunnels ORDER BY id DESC LIMIT 1")
    tunnel = cursor.fetchone()
    print("\n--- 🌐 EXPOSICIÓN PÚBLICA (Cloudflare Tunnel) ---")
    if tunnel:
        print(f"  🔗 URL Activa: {tunnel[0]}")
    else:
        print("  ⚠️ Ningún túnel activo grabado.")

    # 3. Estado de Procesos
    print("\n--- ⚙️ SERVICIOS DEL SISTEMA ---")
    
    # Check FastAPI
    fastapi_on = subprocess.call("pgrep -f uvicorn > /dev/null", shell=True) == 0
    print(f"  1. FastAPI Backend (Puerto 8000): [{'ENCENDIDO' if fastapi_on else 'APAGADO'}]")
    
    # Check Docker VANT
    docker_on = subprocess.call("docker ps | grep superccia_vant_container > /dev/null", shell=True) == 0
    print(f"  2. Docker VANT (Entorno Agentes): [{'ENCENDIDO' if docker_on else 'APAGADO'}]")
    
    # Check Cloudflare
    cf_on = subprocess.call("pgrep -f cloudflared > /dev/null", shell=True) == 0
    print(f"  3. Cloudflare Tunnel (HTTPS):     [{'ENCENDIDO' if cf_on else 'APAGADO'}]")
    print("="*50)
    conn.close()

def start_tunnel():
    print("\n🚀 Arrancando Cloudflare Tunnel en segundo plano...")
    subprocess.call("pkill -f cloudflared", shell=True)
    time.sleep(1)
    
    # Ejecutar en background y capturar log para extraer URL
    log_file = "/tmp/cloudflared.log"
    subprocess.Popen(f"cloudflared tunnel --url http://127.0.0.1:8000 > {log_file} 2>&1 &", shell=True)
    print("⏳ Esperando asignación de URL pública...")
    
    url = None
    for _ in range(15):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                content = f.read()
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if match:
                    url = match.group(0)
                    break
    if url:
        print(f"\n✅ TÚNEL CONECTADO EXITOSAMENTE:")
        print(f"👉 {url}")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO public_tunnels (url) VALUES (?)", (url,))
        conn.commit()
        conn.close()
    else:
        print("❌ Error iniciando túnel o tiempo de espera agotado. Revisa /tmp/cloudflared.log")

def stop_tunnel():
    subprocess.call("pkill -f cloudflared", shell=True)
    print("🛑 Cloudflare Tunnel APAGADO.")

def start_fastapi():
    subprocess.call("fuser -k 8000/tcp 2>/dev/null", shell=True)
    subprocess.Popen(f"nohup uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir {PROJ_DIR} --reload > uvicorn.log 2>&1 &", shell=True)
    print("🚀 FastAPI Backend ENCENDIDO (Puerto 8000).")

def stop_fastapi():
    subprocess.call("pkill -f uvicorn", shell=True)
    print("🛑 FastAPI Backend APAGADO.")

def interactive_menu():
    while True:
        show_status()
        print("\nACCIONES DISPONIBLES:")
        print(" [1] Encender Cloudflare Tunnel (HTTPS Público)")
        print(" [2] Apagar Cloudflare Tunnel")
        print(" [3] Encender FastAPI Backend")
        print(" [4] Apagar FastAPI Backend")
        print(" [5] Encender Docker VANT")
        print(" [6] Apagar Docker VANT")
        print(" [0] Salir del Panel")
        
        choice = input("\nSelecciona una opción [0-6]: ").strip()
        
        if choice == "1":
            start_tunnel()
        elif choice == "2":
            stop_tunnel()
        elif choice == "3":
            start_fastapi()
        elif choice == "4":
            stop_fastapi()
        elif choice == "5":
            subprocess.call("docker start superccia_vant_container", shell=True)
            print("🚀 Docker VANT ENCENDIDO.")
        elif choice == "6":
            subprocess.call("docker stop superccia_vant_container", shell=True)
            print("🛑 Docker VANT APAGADO.")
        elif choice == "0":
            print("¡Hasta luego, CTO!")
            break
        else:
            print("Opción no válida.")
        input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    interactive_menu()
