# -*- coding: utf-8 -*-
import subprocess

def check_container():
    try:
        res = subprocess.check_output(["docker", "ps", "--filter", "name=superccia_vant_container", "--format", "{{.Status}}"]).decode()
        print(f"🐳 Estado Contenedor SuperCCIA: {res.strip() if res else 'Detenido/No Encontrado'}")
    except Exception as e:
        print(f"⚠️ Error al verificar Docker: {e}")

if __name__ == "__main__":
    check_container()
