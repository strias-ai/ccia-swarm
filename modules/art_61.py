#!/usr/bin/env python3
"""
Artefacto 61: CCiA Ollama Scheduler & Network Connectivity Auditor
Descripción: Inspecciona los cerebros de Ollama activos, concurrencia de modelos y socket SMTP/IMAP.
"""
import socket
import urllib.request
import json
import sqlite3

DB_PATH = "/home/k1/ccia_workspace/university.db"
OLLAMA_URL = "http://localhost:11434"

def check_ollama_status():
    print("================================================================================")
    print("🧠 AUDITORÍA DE CEREBROS Y RECURSOS DE OLLAMA")
    print("================================================================================")
    
    # 1. Modelos instalados
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [m['name'] for m in data.get('models', [])]
            print(f"• Estado Servicio Ollama:   ONLINE")
            print(f"• Modelos Disponibles:       {', '.join(models)}")
    except Exception as e:
        print(f"• Estado Servicio Ollama:   OFFLINE / ERROR ({e})")

    # 2. Modelos actualmente cargados en RAM/VRAM
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/ps")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            running = [m['name'] for m in data.get('models', [])]
            print(f"• Modelos en Memoria (RAM):  {running if running else 'Ninguno (Standby)'}")
    except Exception:
        print("• Modelos en Memoria:        No se pudo consultar /api/ps")

def check_email_sockets():
    print("\n================================================================================")
    print("🌐 PRUEBA DE CONEXIÓN A PUERTOS SMTP / IMAP")
    print("================================================================================")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cfg = cur.execute("SELECT imap_server, imap_port, smtp_server, smtp_port, account_email FROM email_config WHERE id=1;").fetchone()
    conn.close()
    
    imap_host, imap_port, smtp_host, smtp_port, email_account = cfg
    
    print(f"• Cuenta Configurada: {email_account}")
    
    # Test IMAP
    try:
        s = socket.create_connection((imap_host, imap_port), timeout=3)
        s.close()
        print(f"• Servidor IMAP ({imap_host}:{imap_port}): REACHABLE (Puerto abierto)")
    except Exception as e:
        print(f"• Servidor IMAP ({imap_host}:{imap_port}): UNREACHABLE ({e})")
        
    # Test SMTP
    try:
        s = socket.create_connection((smtp_host, smtp_port), timeout=3)
        s.close()
        print(f"• Servidor SMTP ({smtp_host}:{smtp_port}): REACHABLE (Puerto abierto)")
    except Exception as e:
        print(f"• Servidor SMTP ({smtp_host}:{smtp_port}): UNREACHABLE ({e})")

if __name__ == "__main__":
    check_ollama_status()
    check_email_sockets()
    print("================================================================================")
