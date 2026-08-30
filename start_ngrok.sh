#!/bin/bash
NGROK_BIN=$(command -v ngrok || echo "/usr/local/bin/ngrok")
exec $NGROK_BIN http 8080 --domain=prone-brittle-approach.ngrok-free.dev
