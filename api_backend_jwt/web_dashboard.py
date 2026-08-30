# -*- coding: utf-8 -*-
import asyncio
import os
import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from telemetry_daemon import collect_metrics

app = FastAPI(title="CCIA University & Telemetry Web Dashboard")
DB_PATH = os.path.join(os.path.dirname(__file__), "university.db")

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>CCIA Mission Control Dashboard</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: monospace; padding: 20px; }
        h1 { color: #38bdf8; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
        pre { background: #090d16; padding: 10px; border-radius: 4px; color: #4ade80; overflow-x: auto; }
        .metric { font-size: 1.2em; color: #facc15; }
    </style>
</head>
<body>
    <h1>🛸 CCIA Mission Control - Dashboard Web Observacional</h1>
    <div class="grid">
        <div class="card">
            <h2>🖥️ Telemetría APU / Sistema</h2>
            <div id="telemetry" class="metric">Cargando métricas...</div>
        </div>
        <div class="card">
            <h2>🏛️ Biblioteca Universitaria</h2>
            <pre id="univ_status">Conectando...</pre>
        </div>
    </div>

    <script>
        const ws = new WebSocket("ws://" + location.host + "/ws/live");
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById("telemetry").innerHTML = 
                "CPU: " + data.telemetry.cpu + "% | RAM: " + data.telemetry.ram + "% (" + data.telemetry.ram_available_mb + " MB libres)<br>Ollama Engine: " + data.telemetry.ollama;
            
            let univTxt = "TESIS APROBADAS Y EXP REGISTRADA:\\n";
            data.skills.forEach(s => {
                univTxt += "• " + s[0] + " (Lvl " + s[1] + ") - Especialidad: " + s[2] + " [" + s[3] + " tesis]\\n";
            });
            document.getElementById("univ_status").innerText = univTxt;
        };
    </script>
</body>
</html>
"""

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    return HTML_LAYOUT

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            metrics = collect_metrics()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT agent_id, level, specialty, approved_count FROM agent_skills")
            skills = cursor.fetchall()
            conn.close()

            payload = {
                "telemetry": metrics,
                "skills": skills
            }
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
