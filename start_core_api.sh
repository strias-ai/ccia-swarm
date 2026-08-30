#!/bin/bash
cd /home/k1/ccia_workspace
export HOME="/home/k1"
export PATH="/home/k1/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONPATH="/home/k1/.local/lib/python3.12/site-packages:/home/k1/ccia_workspace:$PYTHONPATH"
exec python3 -m uvicorn main_api:app --host 0.0.0.0 --port 8000
