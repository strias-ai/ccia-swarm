# -*- coding: utf-8 -*-
"""
<< CCIA SYSTEMD DAEMON MANAGER V1.0.0
"""
import subprocess
import os

SERVICES = {
    "ccia-backend": """[Unit]
Description=CCIA FastAPI Backend Engine
After=network.target

[Service]
User=k1
WorkingDirectory=/home/k1/ccia_workspace/api_backend_jwt
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
""",
    "ccia-ngrok": """[Unit]
Description=CCIA Ngrok Persistent Tunnel
After=network.target ccia-backend.service

[Service]
User=k1
ExecStart=/usr/local/bin/ngrok http --domain=prone-brittle-approach.ngrok-free.dev 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
}

def install_systemd_services():
    for name, content in SERVICES.items():
        path = f"/tmp/{name}.service"
        with open(path, "w") as f:
            f.write(content)
        subprocess.run(f"sudo mv {path} /etc/systemd/system/{name}.service", shell=True)
    
    subprocess.run("sudo systemctl daemon-reload", shell=True)
    subprocess.run("sudo systemctl enable ccia-backend ccia-ngrok", shell=True)
    return {"status": "SUCCESS", "services_installed": list(SERVICES.keys())}

if __name__ == "__main__":
    print("⚙️ Configurando servicios Systemd para ejecución 24/7...")
    res = install_systemd_services()
    print("✅ Servicios registrados en el sistema operativo:", res)
